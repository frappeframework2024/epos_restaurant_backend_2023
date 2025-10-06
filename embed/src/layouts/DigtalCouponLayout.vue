<template> 
  <div class="layout">
 
    <!-- Sidebar + Content -->
    <div class="main"> 
      <section class="content">
        <!-- This is where page content will be injected -->
        <slot />
      </section>
    </div>
 
    <!-- Footer -->
    <footer class="footer w-20rem">
        <nav class="flex justify-content-around mx-auto w-full">
          <router-link class="flex flex-column align-items-center flex-1 text-sm" to="/embed/ecoupon">
            <div><ComIcon icon="homeIcon"></ComIcon></div>
            <div>{{ t("Home") }}</div>
          </router-link>
          <router-link class="flex flex-column align-items-center flex-1 text-sm" to="/embed/ecoupon/transaction">
            <div><ComIcon icon="transactionIcon"></ComIcon></div>
            <div>{{ t("Transactions") }}</div>
          </router-link>
          <router-link class="flex flex-column align-items-center flex-1 text-sm" to="/embed/ecoupon/my-account">
            <div><ComIcon icon="myAccountIcon"></ComIcon></div>
            <div>{{ t("My Account") }}</div>
          </router-link>
        </nav>
    </footer>
  </div>
</template>

<script setup>
const t = window.t;
</script>

<style scoped>
.layout {
  display: flex;
  flex-direction: column;
  height: 100vh;
} 

.footer {
  background-color: rgba(255, 255, 255, 0.15); /* White with 15% opacity */
  padding: 10px;
  text-align: center;
  box-shadow: rgba(0, 0, 0, 0.24) 0px 3px 8px;
  border-radius: 50px;
  margin-bottom: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px); /* Adjust blur strength as needed */
  -webkit-backdrop-filter: blur(10px); /* For Safari compatibility */
  position: fixed;
  bottom: 0;
  z-index: 1000;
  left: 50%;
  transform: translateX(-50%);
  width:100%;
  max-width: 28rem;
}
.sidebar {
  width: 200px;
  background: #f4f4f4;
  padding: 1rem;
}
.footer a {
  text-decoration: none;
  color: #A0A8B3; /* inactive */
  transition: color 0.3s ease;
  padding-top: 5px;
  padding-bottom: 5px;
  outline: none;
  -webkit-tap-highlight-color: transparent;
}
.footer a.router-link-active {

  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border-radius: 30px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding-top: 5px;
  padding-bottom: 5px;
  background: linear-gradient(90deg, #4FACFE, #00F2FE);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
</style>
