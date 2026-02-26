<template>

    {{ data }}

    {{ auth }}
    <hr>
    {{ currentUser }}

    <Button @click="onLogin">Login</Button>
    <Button @click="onLogout">Logout</Button>
</template>
<script setup>
import { ref, onMounted } from 'vue'
const auth = ref(window.auth)
const data = ref()

const currentUser= ref()

onMounted(()=>{
    window.db.getDocList("Customer").then(r=>{
        data.value = r
    })

    window.auth.getLoggedInUser()
  .then((user) => 
  {
    currentUser.value = user
  }
  )
  .catch((error) => console.error(error));
})

function onLogin(){ 
    window.auth
  .loginWithUsernamePassword({ username: 'Administrator', password: '123456' })
  .then((response) => alert("login succesas"))
  .catch((error) => console.error(error));
}

function onLogout(){
    window.auth
  .logout()
  .then(() => {
    window.location="/"
  })
  .catch((error) => console.error(error));
}


</script>