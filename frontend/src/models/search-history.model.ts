import { Model } from '@vuex-orm/core'

export interface ISearchHistoryState {
}

export interface ISearch {
  key: string
  date: number
}

export default class SearchHistory extends Model implements ISearch {
  static entity = 'search-history'
  static primaryKey = 'key'
  public readonly key!: string
  public readonly date!: number

  static fields() {
    return {
      key: this.attr(''),
      date: this.attr(0)
    }
  }

  static get $state(): ISearchHistoryState {
    return this.store().state.entities[this.entity]
  }

  static state(): ISearchHistoryState {
    return {
    }
  }

  public static log(key: string) {
    SearchHistory.insert({ data: { key, date: Date.now() } })
  }

  public static searchHints(searchString: string): IHint[] {
    if (!(searchString?.trim())) {
      return this.all()
        .sort((a, b) => b.date - a.date)
        .map(entry => ({ type: 'local', key: entry.key }))
        .slice(0, 10) as IHint[]
    }

    const str = searchString.trim()

    return this.all()
      .filter((entry: ISearch) => {
        const val = entry.key.toLowerCase()
        return val.includes(str.toLowerCase()) &&
          val.length > str.length
      })
      .sort((a, b) => b.date - a.date)
      .map(entry => ({ type: 'local', key: entry.key })) || []
  }

  public static deleteHint(key: string) {
    this.delete(key)
  }
}