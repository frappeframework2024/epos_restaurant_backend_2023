var C=(N,y,f)=>new Promise((z,v)=>{var L=n=>{try{u(f.next(n))}catch(b){v(b)}},o=n=>{try{u(f.throw(n))}catch(b){v(b)}},u=n=>n.done?z(n.value):Promise.resolve(n.value).then(L,o);u((f=f.apply(N,y)).next())});import{_ as F,i as S,u as G,a as K,r as Q,b as X,c as E,d as Y,w as a,e as m,o as j,f as t,g as s,h as r,t as g,n as Z,j as ee,k as c,l as se,m as te,p as I,A as oe}from"./index-a9d86003.js";const ne={class:"h-full w-full p-10 flex justify-center items-center"},ie={class:"app-info w-96 inline-block text-center rounded-lg pa-4 bg-gradient-to-t from-yellow-900 to-yellow-700 text-white shadow-sm"},ae={class:"mb-3"},le=["src"],re={class:"font-bold mb-3"},de={class:"py-3"},ce={class:"h-full flex items-center justify-center bg-gray-100"},ue=["onSubmit"],pe={class:"w-73"},_e={class:"d-block d-md-none mt-4"},me={class:"mb-3"},ge=["src"],fe={class:"text-center mb-3"},ve={class:"font-bold mb-1 text-2xl"},be={class:"text-sm"},we={class:"mb-3"},he={class:"relative"},xe={class:"grid grid-cols-3 gap-3"},ke={class:"mt-6"},ye={class:"mt-4 text-center"},$e={class:"text-sm text-green-700"},Ce={key:0,class:"fixed bottom-8"},Se={__name:"Login",setup(N){S("$moment");const y=S("$gv"),f=S("$sale"),{mobile:z}=G(),v=oe(),L=K();let o=Q({username:"",password:""});const u=X(),n=E(()=>JSON.parse(localStorage.getItem("setting"))),b=E(()=>u.state.isLoading),D=S("$auth");u.state.isLoading=!1;function p(i){o.password==null&&(o.password=""),o.password=o.password+i}function O(){o.password=""}function A(){return localStorage.getItem("is_window")=="1"}function J(){o.password=o.password.substring(0,o.password.length-1)}const M=()=>C(this,null,function*(){if(!o.password){v.warning("Invalid Password",{position:"top"});return}u.dispatch("startLoading"),I({url:"epos_restaurant_2023.api.api.check_username",auto:!0,params:{pin_code:o.password},onSuccess(e){return C(this,null,function*(){u.dispatch("startLoading"),o.username=e.username,o.username&&o.password&&((yield D.login(o.username,o.password))?(R(e),U()):(v.warning("Login fail. Invalid username or password."),u.dispatch("endLoading")))})},onError(e){u.dispatch("endLoading")}})});function R(i){I({url:"epos_restaurant_2023.api.api.get_user_information",auto:!0,onSuccess(_){return C(this,null,function*(){_.permission=i.permission,localStorage.setItem("current_user",JSON.stringify(_)),L.push({name:"Home"}),u.dispatch("endLoading")})},onError(_){u.dispatch("endLoading")}})}function U(){I({url:"epos_restaurant_2023.api.promotion.check_promotion",cache:"check_promotion",auto:!0,params:{business_branch:y.setting.business_branch},onSuccess(i){y.promotion=i,f.promotion=i}})}function W(){const i={action:"exit"};window.chrome.webview.postMessage(JSON.stringify(i))}return(i,e)=>{const _=m("v-divider"),$=m("v-list-item"),H=m("v-list"),V=m("v-col"),T=m("v-text-field"),d=m("v-btn"),q=m("v-row");return j(),Y(q,{class:"mt-0 mb-0 h-screen"},{default:a(()=>[t(V,{md:"6",lg:"8",class:"pa-0 d-sm-none d-none d-md-block"},{default:a(()=>{var w,h,x;return[s("div",{class:"h-screen bg-cover bg-no-repeat bg-center",style:Z({"background-image":"url("+((w=r(n))==null?void 0:w.login_background)+")"})},[s("div",ne,[s("div",null,[s("div",ie,[s("div",ae,[s("img",{class:"my-0 mx-auto",src:(h=r(n))==null?void 0:h.logo},null,8,le)]),s("h1",re,g((x=r(n))==null?void 0:x.app_name),1),t(_),s("div",de,[t(H,{lines:"one","bg-color":"transparent"},{default:a(()=>{var k,l,B,P;return[t($,{class:"mb-2",title:(k=r(n))==null?void 0:k.business_branch,subtitle:i.$t("Business")},null,8,["title","subtitle"]),t($,{class:"mb-2",title:(l=r(n))==null?void 0:l.pos_profile,subtitle:i.$t("POS Profile")},null,8,["title","subtitle"]),t($,{class:"mb-2",title:(B=r(n))==null?void 0:B.phone_number,subtitle:i.$t("Phone Number")},null,8,["title","subtitle"]),t($,{title:(P=r(n))==null?void 0:P.address,subtitle:i.$t("Address")},null,8,["title","subtitle"])]}),_:1})])])])])],4)]}),_:1}),t(V,{sm:"12",md:"6",lg:"4",class:"pa-0 relative"},{default:a(()=>{var w,h,x,k;return[s("div",ce,[s("form",{onSubmit:ee(M,["prevent"])},[s("div",pe,[s("div",null,[s("div",_e,[s("div",me,[s("img",{class:"my-0 mx-auto w-16",src:(w=r(n))==null?void 0:w.logo},null,8,ge)]),s("div",fe,[s("h1",ve,g((h=r(n))==null?void 0:h.app_name),1),s("p",be,g((x=r(n))==null?void 0:x.business_branch),1),t(_)])]),s("div",we,[s("div",he,[t(T,{readonly:r(z),type:"password",density:"compact",variant:"solo",autofocus:"",label:i.$t("Password"),"append-inner-icon":"mdi-arrow-left","single-line":"","hide-details":"",modelValue:r(o).password,"onUpdate:modelValue":e[0]||(e[0]=l=>r(o).password=l),height:"200","onClick:appendInner":e[1]||(e[1]=l=>J())},null,8,["readonly","label","modelValue"])])]),s("div",null,[s("div",xe,[t(d,{onClick:e[2]||(e[2]=l=>p("1")),size:"x-large"},{default:a(()=>[c(" 1 ")]),_:1}),t(d,{onClick:e[3]||(e[3]=l=>p("2")),size:"x-large"},{default:a(()=>[c(" 2 ")]),_:1}),t(d,{onClick:e[4]||(e[4]=l=>p("3")),size:"x-large"},{default:a(()=>[c(" 3 ")]),_:1}),t(d,{onClick:e[5]||(e[5]=l=>p("4")),size:"x-large"},{default:a(()=>[c(" 4 ")]),_:1}),t(d,{onClick:e[6]||(e[6]=l=>p("5")),size:"x-large"},{default:a(()=>[c(" 5 ")]),_:1}),t(d,{onClick:e[7]||(e[7]=l=>p("6")),size:"x-large"},{default:a(()=>[c(" 6 ")]),_:1}),t(d,{onClick:e[8]||(e[8]=l=>p("7")),size:"x-large"},{default:a(()=>[c(" 7 ")]),_:1}),t(d,{onClick:e[9]||(e[9]=l=>p("8")),size:"x-large"},{default:a(()=>[c(" 8 ")]),_:1}),t(d,{onClick:e[10]||(e[10]=l=>p("9")),size:"x-large"},{default:a(()=>[c(" 9 ")]),_:1}),t(d,{onClick:e[11]||(e[11]=l=>p("0")),size:"x-large"},{default:a(()=>[c(" 0 ")]),_:1}),t(d,{class:"col-span-2",color:"error",onClick:O,size:"x-large"},{default:a(()=>[c(g(i.$t("Clear")),1)]),_:1})])]),s("div",ke,[t(d,{type:"submit",loading:r(b),size:"x-large",class:"w-full",color:"primary"},{default:a(()=>[c(g(i.$t("Login")),1)]),_:1},8,["loading"])]),s("div",ye,[s("p",$e,g((k=r(n))==null?void 0:k.pos_profile),1)])])])],40,ue),A()?(j(),se("div",Ce,[t(d,{block:"",class:"w-full","prepend-icon":"mdi-window-close",size:"x-large",color:"error",onClick:e[12]||(e[12]=l=>W())},{default:a(()=>[c(g(i.$t("Exit")),1)]),_:1})])):te("",!0)])]}),_:1})]),_:1})}}},Ie=F(Se,[["__scopeId","data-v-6bb7af1a"]]);export{Ie as default};
