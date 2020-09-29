<template>
  <footer class="footer px-4 mx-2">
    <div class="row align-items-center justify-content-lg-between">
      <div class="col-lg-6">
        <div class="copyright text-center text-black-50 text-lg-right">
          © {{year}} <a href="https://www.educalegal.com.br" class="font-weight-bold ml-1" target="_blank" rel="noopener">Educa Legal</a> - Versão 2.0
        </div>
      </div>
    </div>
  </footer>
</template>
<script>
export default {
  data() {
    return {
      year: new Date().getFullYear()
    };
  }
};
</script>
<style></style>
