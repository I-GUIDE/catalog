import '@/assets/css/global.scss'

import Vuex from 'vuex'
import VuexORM from '@vuex-orm/core'
import createPersistedState from 'vuex-persistedstate'
import VueCookies from 'vue-cookies'
import Vue from 'vue'
import App from './App.vue'
import vuetify from '@/plugins/vuetify'
import browserDetect from "vue-browser-detect-plugin"
import VueRouter from 'vue-router'
import VueI18n from 'vue-i18n'

import { router } from './router/router'
import { orm } from '@/models/orm'
import { persistedPaths } from './models/persistedPaths'
import { APP_NAME } from './constants'
import { messages } from './i18n/messages'

// Uncomment to filter out errors
// Vue.config.errorHandler = (err, vm, info) => {
  //   if (process.env.NODE_ENV !== 'production') {
    //     // Show any error but this one
    //     if (err.message !== "Some error you want to leave out") {
      //       console.error(err)
      //     }
      //   }
      // }
      
Vue.config.productionTip = false
Vue.use(Vuex)

// Create Vuex Store and register database through Vuex ORM.
const store = new Vuex.Store({
  plugins: [
    VuexORM.install(orm),
    createPersistedState({
      paths: persistedPaths,
      key: APP_NAME
    })
  ]
})
      
Vue.use(VueCookies)
Vue.use(VueRouter)
Vue.use(browserDetect)
Vue.use(VueI18n)

// Create VueI18n instance
const i18n = new VueI18n({
  locale: 'en',
  fallbackLocale: 'en',
  messages,
})

new Vue({
  store,
  vuetify,
  router,
  i18n,
  render: (h) => h(App)
}).$mount('#app')