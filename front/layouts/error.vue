<template>
  <div class="bg-default">
    <!-- Header -->
    <div class="header bg-success py-7 py-lg-8 pt-lg-9">
      <div class="container">
        <div class="header-body text-center mb-7">
          <div class="row justify-content-center">
            <div class="col-xl-5 col-lg-6 col-md-8 px-5">
              <h1 class="text-white">Ooops!</h1>
              <h2 class="text-white">Página não encontrada...</h2>
              <nuxt-link to="/painel" class="font-weight-bold text-white mt-5">Voltar para o painel</nuxt-link>
            </div>
          </div>
        </div>
      </div>
      <div class="separator separator-bottom separator-skew zindex-100">
        <svg x="0" y="0" viewBox="0 0 2560 100" preserveAspectRatio="none" version="1.1" xmlns="http://www.w3.org/2000/svg">
          <polygon class="fill-default" points="2560 0 2560 100 0 100"></polygon>
        </svg>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  layout: 'AuthLayout'
}
</script>
