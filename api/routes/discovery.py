from datetime import datetime
from typing import Union

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel, validator

router = APIRouter()


class SearchQuery(BaseModel):
    term: str
    sortBy: str = None
    contentType: str = None
    providerName: str = None
    creatorName: str = None
    dataCoverageStart: int = None
    dataCoverageEnd: int = None
    publishedStart: int = None
    publishedEnd: int = None
    variableMeasured: str = None
    includedInDataCatalogName: str = None
    hasPartName: str = None
    isPartOfName: str = None
    associatedMediaName: str = None
    fundingGrantName: str = None
    fundingFunderName: str = None
    clusters: Union[list[str], None] = Query(default=None)  # TODO: may be this is not relevant to iguide
    pageNumber: int = 1
    pageSize: int = 30

    @validator('*')
    def empty_str_to_none(cls, v, field, **kwargs):
        if field.name == 'term':
            return v.strip()

        if isinstance(v, str) and v.strip() == '':
            return None
        return v

    @validator('dataCoverageStart', 'dataCoverageEnd', 'publishedStart', 'publishedEnd')
    def validate_year(cls, v, values, field, **kwargs):
        try:
            datetime(v, 1, 1)
        except ValueError:
            raise ValueError(f'{field.name} is not a valid year')
        if field.name == 'dataCoverageEnd':
            if 'dataCoverageStart' in values and v <= values['dataCoverageStart']:
                raise ValueError(f'{field.name} must be greater or equal to dataCoverageStart')
        if field.name == 'publishedEnd':
            if 'publishedStart' in values and v <= values['publishedStart']:
                raise ValueError(f'{field.name} must be greater or equal to publishedStart')
        return v

    @validator('pageNumber', 'pageSize')
    def validate_page(cls, v, field, **kwargs):
        if v <= 0:
            raise ValueError(f'{field.name} must be greater than 0')
        return v

    @property
    def _filters(self):
        filters = []
        if self.publishedStart:
            filters.append(
                {
                    'range': {
                        'path': 'datePublished',
                        'gte': datetime(self.publishedStart, 1, 1),
                    },
                }
            )
        if self.publishedEnd:
            filters.append(
                {
                    'range': {
                        'path': 'datePublished',
                        'lt': datetime(self.publishedEnd + 1, 1, 1),  # +1 to include all of the publishedEnd year
                    },
                }
            )
        if self.dataCoverageStart:
            filters.append(
                {'range': {'path': 'temporalCoverageDates.0', 'gte': datetime(self.dataCoverageStart, 1, 1)}}
            )
        if self.dataCoverageEnd:
            filters.append(
                {'range': {'path': 'temporalCoverageDates.1', 'lt': datetime(self.dataCoverageEnd + 1, 1, 1)}}
            )
        return filters

    @property
    def _should(self):
        auto_complete_paths = ['name', 'description', 'keywords']
        should = [
            {'autocomplete': {'query': self.term, 'path': key, 'fuzzy': {'maxEdits': 1}}} for key in auto_complete_paths
        ]
        return should

    @property
    def _must(self):
        must = []
        if self.creatorName:
            must.append({'text': {'path': 'creator.@list.name', 'query': self.creatorName}})
        if self.providerName:
            must.append({'text': {'path': 'provider.name', 'query': self.providerName}})
        if self.contentType:
            must.append({'term': {'path': '@type', 'value': self.contentType}})
        if self.variableMeasured:
            must.append({'term': {'path': 'variableMeasured', 'value': self.variableMeasured}})
        if self.includedInDataCatalogName:
            must.append({'text': {'path': 'includedInDataCatalog.@list.name', 'query': self.includedInDataCatalogName}})
        if self.hasPartName:
            must.append({'text': {'path': 'hasPart.@list.name', 'query': self.hasPartName}})
        if self.isPartOfName:
            must.append({'text': {'path': 'isPartOf.@list.name', 'query': self.isPartOfName}})
        if self.associatedMediaName:
            must.append({'text': {'path': 'associatedMedia.@list.name', 'query': self.associatedMediaName}})
        if self.fundingGrantName:
            must.append({'text': {'path': 'funding.@list.grant.name', 'query': self.fundingGrantName}})
        if self.fundingFunderName:
            must.append({'text': {'path': 'funding.@list.funder.name', 'query': self.fundingFunderName}})

        return must

    @property
    def stages(self):
        highlightPaths = ['name', 'description', 'keywords', 'creator.@list.name']
        stages = []
        if self.dataCoverageStart or self.dataCoverageEnd:
            stages.append(
                {
                    '$addFields': {
                        'dataCoverageDates': {
                            '$map': {
                                'input': {'$split': ['$dataCoverage', '/']},
                                'in': {'$dateFromString': {'dateString': '$$this', 'onError': datetime.utcnow()}},
                            }
                        }
                    }
                }
            )

        stages.append(
            {
                '$search': {
                    'index': 'fuzzy_search',
                    'compound': {'filter': self._filters, 'should': self._should, 'must': self._must},
                    'highlight': {'path': highlightPaths},
                }
            }
        )

        if self.clusters:
            stages.append({'$match': {'clusters': {'$all': self.clusters}}})

        # sorting needs to happen before pagination
        if self.sortBy:
            stages.append({'$sort': {self.sortBy: 1}})
        stages.append({'$skip': (self.pageNumber - 1) * self.pageSize})
        stages.append({'$limit': self.pageSize})
        stages.append({'unset': ['_id']})
        stages.append(
            {'$set': {'score': {'$meta': 'searchScore'}, 'highlights': {'$meta': 'searchHighlights'}}},
        )
        return stages


@router.get("/search")
async def search(request: Request, search_query: SearchQuery):
    stages = search_query.stages
    result = await request.app.mongodb["catalog"].aggregate(stages).to_list(search_query.pageSize)
    return result


@router.get("/typeahead")
async def typeahead(request: Request, term: str, pageSize: int = 30):
    autoCompletePaths = ['name', 'description', 'keywords']
    highlightsPaths = ['name', 'description', 'keywords']
    should = [{'autocomplete': {'query': term, 'path': key, 'fuzzy': {'maxEdits': 1}}} for key in autoCompletePaths]

    stages = [
        {
            '$search': {
                'index': 'fuzzy_search',
                'compound': {'should': should},
                'highlight': {'path': ['description', 'name', 'keywords']},
            }
        },
        {
            '$project': {
                'name': 1,
                'description': 1,
                'keywords': 1,
                'highlights': {'$meta': 'searchHighlights'},
                '_id': 0,
            }
        },
    ]
    result = await request.app.mongodb["typeahead"].aggregate(stages).to_list(pageSize)
    return result
