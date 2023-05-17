import json
from datetime import datetime
from typing import Union

import pandas
from fastapi import APIRouter, Query, Request
from fastapi.responses import FileResponse

router = APIRouter()


@router.get("/search")
async def search(request: Request, term: str, sortBy: str = None, contentType: str = None, providerName: str = None,
                 creatorName: str = None, dataCoverageStart: int = None, dataCoverageEnd: int = None,
                 publishedStart: int = None, publishedEnd: int = None, variableMeasured: str = None,
                 includedInDataCatalogName: str = None, hasPartName: str = None, isPartOfName: str = None,
                 associatedMediaName: str = None, fundingGrantName: str = None, fundingFunderName: str = None,
                 clusters: Union[list[str], None] = Query(default=None),
                 pageNumber: int = 1, pageSize: int = 30):
    searchPaths = ['name', 'description', 'keywords']
    highlightPaths = ['name', 'description', 'keywords', 'creator.@list.name']
    autoCompletePaths = ['name', 'description', 'keywords']

    should = [{'autocomplete': {'query': term, 'path': key, 'fuzzy': {'maxEdits': 1}}} for key in autoCompletePaths]
    must = []
    stages = []
    filters = []

    if publishedStart:
        filters.append({
            'range': {
                'path': 'datePublished',
                'gte': datetime(publishedStart, 1, 1),
            },
        })

    if publishedEnd:
        filters.append({
            'range': {
                'path': 'datePublished',
                'lt': datetime(publishedEnd + 1, 1, 1)  # +1 to include all of the publishedEnd year
            },
        })

    if dataCoverageStart:
        # TODO: split the date string on the '/' character and get the start date
        #  example value for temporalCoverage: "2020-01-01T00:00:00Z/2020-12-31T23:59:59Z"
        filters.append({
            'range': {
                'path': 'temporalCoverage.start',
                'gte': datetime(dataCoverageStart, 1, 1)
            }
        })

    if dataCoverageEnd:
        # TODO: split the date string on the '/' character and get the end date
        #  example value for temporalCoverage:
        #   "2020-01-01T00:00:00Z/2020-12-31T23:59:59Z"
        #  OR
        #   "2020-01-01T00:00:00Z/.."
        filters.append({
            'range': {
                'path': 'temporalCoverage.end',
                'lt': datetime(dataCoverageEnd + 1, 1, 1)
            }
        })

    if creatorName:
        must.append({
            'text': {
                'path': 'creator.@list.name',
                'query': creatorName
            }
        })

    if providerName:
        must.append({
            'text': {
                'path': 'provider.name',
                'query': providerName
            }
        })

    if contentType:
        must.append({
            'text': {
                'path': '@type',
                'query': contentType
            }
        })

    if variableMeasured:
        must.append({
            'text': {
                'path': 'variableMeasured',
                'query': variableMeasured
            }
        })

    if includedInDataCatalogName:
        must.append({
            'text': {
                'path': 'includedInDataCatalog.@list.name',
                'query': includedInDataCatalogName
            }
        })

    if hasPartName:
        must.append({
            'text': {
                'path': 'hasPart.@list.name',
                'query': hasPartName
            }
        })

    if isPartOfName:
        must.append({
            'text': {
                'path': 'isPartOf.@list.name',
                'query': isPartOfName
            }
        })

    if associatedMediaName:
        must.append({
            'text': {
                'path': 'associatedMedia.@list.name',
                'query': associatedMediaName
            }
        })

    if fundingGrantName:
        must.append({
            'text': {
                'path': 'funding.@list.grant.name',
                'query': fundingGrantName
            }
        })

    if fundingFunderName:
        must.append({
            'text': {
                'path': 'funding.@list.funder.name',
                'query': fundingFunderName
            }
        })

    stages.append(
        {
            '$search': {
                'index': 'fuzzy_search',
                'compound': {
                    'filter': filters,
                    'should': should,
                    'must': must
                },
                'highlight': {'path': highlightPaths}
            }
        }
    )

    if clusters:
        stages.append({
            '$match': {
                'clusters': {
                    '$all': clusters
                }
            }
        })

    # Sort needs to happen before pagination
    if sortBy:
        stages.append({
            '$sort': {
                sortBy: 1
            }
        })

    stages.append(
        {
            '$skip': (pageNumber - 1) * pageSize
        }
    )
    stages.append(
        {
            '$limit': pageSize
        },
    )
    stages.append(
        {
            '$unset': ['_id']
        }
    )
    stages.append(
        {
            '$set': {
                'score': {'$meta': 'searchScore'},
                'highlights': {'$meta': 'searchHighlights'}
            }
        },
    )

    result = await request.app.mongodb["cznet"].aggregate(stages).to_list(pageSize)
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
                'compound': {
                    'should': should
                },
                'highlight': {
                    'path': ['description', 'name', 'keywords']
                }
            }
        }, {
            '$project': {
                'name': 1,
                'description': 1,
                'keywords': 1,
                'highlights': {
                    '$meta': 'searchHighlights'
                },
                '_id': 0
            }
        }
    ]
    result = await request.app.mongodb["cznet"].aggregate(stages).to_list(pageSize)
    return result


@router.get("/csv")
async def sanitize(request: Request):
    project = [{
        '$project': {
            'name': 1,
            'description': 1,
            'keywords': 1,
            '_id': 0
        }
    }]
    json_response = await request.app.mongodb["cznet"].aggregate(project).to_list(None)
    df = pandas.read_json(json.dumps(json_response))
    filename = "file.csv"
    df.to_csv(filename)
    return FileResponse(filename, filename=filename, media_type='application/octet-stream')


@router.get("/clusters", response_model=list[str])
async def clusters(request: Request):
    return request.app.clusters
