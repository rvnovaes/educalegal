<template>
  <div :class="layoutClass" class="auth-layout">

    <div class="main-content">
        <nuxt></nuxt>
    </div>

    <footer class="py-5" id="footer-main">
      <div class="container">
        <div class="row align-items-center justify-content-xl-between">
          <div class="col-xl-12">
            <div class="copyright text-center text-black-50 text-lg-right">
              © {{year}} <a href="https://www.educalegal.com.br" class="font-weight-bold text-white ml-1" target="_blank" rel="noopener">Educa Legal</a> - Versão 2.0.1
            </div>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>
<script>

  export default {
    props: {
      backgroundColor: {
        type: String,
        default: 'black'
      }
    },
    data() {
      return {
        // showMenu: false,
        menuTransitionDuration: 250,
        year: new Date().getFullYear(),
        pageClass: 'login-page',
      };
    },
    computed: {
      title() {
        return `${this.$route.name} Page`;
      },
      layoutClass() {
        let exceptions = ['home']
        if (!exceptions.includes(this.$route.name)) {
          return 'bg-primary'
        } else {
          return ''
        }
      }
    },
  };
</script>
<style lang="scss">
  .auth-layout {
    min-height: 100vh;
  }
</style>
