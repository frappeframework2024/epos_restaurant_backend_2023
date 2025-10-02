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
    <footer class="footer">
        <nav class="flex justify-content-around mx-auto w-full">
          <router-link class="flex flex-column align-items-center flex-1 text-sm" to="/embed/ecoupon">
            <div><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M12 15L12 18" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"></path> <path d="M22 12.2039V13.725C22 17.6258 22 19.5763 20.8284 20.7881C19.6569 22 17.7712 22 14 22H10C6.22876 22 4.34315 22 3.17157 20.7881C2 19.5763 2 17.6258 2 13.725V12.2039C2 9.91549 2 8.77128 2.5192 7.82274C3.0384 6.87421 3.98695 6.28551 5.88403 5.10813L7.88403 3.86687C9.88939 2.62229 10.8921 2 12 2C13.1079 2 14.1106 2.62229 16.116 3.86687L18.116 5.10812C20.0131 6.28551 20.9616 6.87421 21.4808 7.82274" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"></path> </g></svg></div>
            <div>Home</div>
          </router-link>
          <router-link class="flex flex-column align-items-center flex-1 text-sm" to="/embed/ecoupon/transaction">
            <div><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path d="M5.88889 3.75C6.3031 3.75 6.63889 3.41421 6.63889 3C6.63889 2.58579 6.3031 2.25 5.88889 2.25V3.75ZM10 2.25C9.58579 2.25 9.25 2.58579 9.25 3C9.25 3.41421 9.58579 3.75 10 3.75V2.25ZM18.1111 3.75C19.8214 3.75 21.25 5.19049 21.25 7.02036H22.75C22.75 4.40946 20.6964 2.25 18.1111 2.25V3.75ZM5.88889 2.25C3.30359 2.25 1.25 4.40946 1.25 7.02036H2.75C2.75 5.19049 4.17864 3.75 5.88889 3.75V2.25ZM21.25 7.02036C21.25 8.68726 20.0607 10.0357 18.557 10.2581L18.7764 11.7419C21.0419 11.4069 22.75 9.40421 22.75 7.02036H21.25ZM5.44305 10.2581C3.93934 10.0357 2.75 8.68726 2.75 7.02036H1.25C1.25 9.40422 2.95811 11.4069 5.22362 11.7419L5.44305 10.2581ZM10 3.75H18.1111V2.25H10V3.75Z" fill="#1C274C"></path> <path d="M12 9V14M12 14L14 11.6667M12 14L10 11.6667" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> <path d="M5 10C5 8.11438 5 7.17157 5.58579 6.58579C6.17157 6 7.11438 6 9 6H15C16.8856 6 17.8284 6 18.4142 6.58579C19 7.17157 19 8.11438 19 10V16C19 17.8856 19 18.8284 18.4142 19.4142C17.8284 20 16.8856 20 15 20H9C7.11438 20 6.17157 20 5.58579 19.4142C5 18.8284 5 17.8856 5 16V10Z" stroke="#1C274C" stroke-width="1.5"></path> <path d="M5 17H13M19 17H17" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"></path> </g></svg></div>
            <div>Transaction</div>
          </router-link>
          <router-link class="flex flex-column align-items-center flex-1 text-sm" to="/embed/ecoupon/my-account">
            <div><svg width="30px" height="30px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <circle cx="12" cy="9" r="3" stroke="#1C274C" stroke-width="1.5"></circle> <path d="M17.9691 20C17.81 17.1085 16.9247 15 11.9999 15C7.07521 15 6.18991 17.1085 6.03076 20" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"></path> <path d="M7 3.33782C8.47087 2.48697 10.1786 2 12 2C17.5228 2 22 6.47715 22 12C22 17.5228 17.5228 22 12 22C6.47715 22 2 17.5228 2 12C2 10.1786 2.48697 8.47087 3.33782 7" stroke="#1C274C" stroke-width="1.5" stroke-linecap="round"></path> </g></svg></div>
            <div>My Account</div>
          </router-link>
        </nav>
    </footer>
  </div>
</template>

<script setup>

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
  margin: 1rem;
  border: 1px solid rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px); /* Adjust blur strength as needed */
  -webkit-backdrop-filter: blur(10px); /* For Safari compatibility */
}
.sidebar {
  width: 200px;
  background: #f4f4f4;
  padding: 1rem;
}

.main {
  flex: 1;
  padding: 1rem;
}
.footer a {
  text-decoration: none;
  color:var(--blue-300);
}
</style>
