import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import km from './locales/km.json'

const i18n = createI18n({
  legacy: false,
  locale: getDefaultLanguage(),
  fallbackLocale: getDefaultLanguage(),
  messages: {
    en,
    km
  }
})

function getDefaultLanguage(){
  return localStorage.getItem("lang") || "km"
}


export default i18n