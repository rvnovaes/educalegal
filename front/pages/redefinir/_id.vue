<template>
  <div>
    <!-- Header -->
    <div class="header bg-gradient-secondary py-7 py-lg-7 pt-lg-9">
      <div class="container">
        <div class="header-body text-center mb-7">
          <div class="row justify-content-center">
            <div class="col-xl-5 col-lg-6 col-md-8 px-5">
              <img src="img/brand/logo_educa_legal.png" alt="Logo Educa Legal">
              <p class="text-lead">Advocacia Virtual para Escolas</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Page content -->
    <div class="container mt--8 pb-5">
      <div class="row justify-content-center">
        <div class="col-lg-5 col-md-7">
          <div class="card bg-secondary border-0 mb-0">

            <div class="card-body px-lg-5 py-lg-5">
              <div class="text-center text-muted mb-4">
                <small>Digite duas vezes sua nova senha:</small>
              </div>
              <validation-observer v-slot="{handleSubmit}" ref="formValidator">
                <form role="form" @submit.prevent="handleSubmit(onSubmit)">
                  <base-input alternative
                              class="mb-3"
                              name="Senha"
                              :rules="{required: true, min: 6}"
                              prepend-icon="ni ni-lock-circle-open"
                              type="password"
                              placeholder="Senha"
                              v-model="password1">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              name="Repita a Senha"
                              :rules="{required: true, min: 6}"
                              prepend-icon="ni ni-lock-circle-open"
                              type="password"
                              placeholder="Repita a senha"
                              v-model="password2">
                  </base-input>

                  <div class="text-center">
                    <base-button type="primary" native-type="submit" class="my-4">Enviar</base-button>
                  </div>
                </form>
              </validation-observer>
            </div>
          </div>
          <div class="row mt-3">
            <div class="col-6">
              <n-link to="/" class="text-light"><small>Entrar no sistema</small></n-link>
            </div>
            <div class="col-6 text-right">
              <n-link to="/registrar" class="text-light"><small>Cria nova conta</small></n-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script>

import Swal from "sweetalert2";

export default {
  layout: "AuthLayout",
  auth: false,

  data() {
    return {
      key: this.$route.params.id,
      password1: null,
      password2: null
    };
  },
  methods: {
    async onSubmit() {
      if (this.password1 !== this.password2) {
        await Swal.fire({
          title: "Tente novamente!",
          text: "As duas senhas digitadas não são iguais...",
          icon: "error",
          customClass: {
            confirmButton: "btn btn-info btn-fill",
          },
          confirmButtonText: "OK",
          showCloseButton: true,
          buttonsStyling: false
        });
      } else {
        try {
          const res = await this.$axios.post("/v2/reset_password/",
            {password: this.password1,
                  key: this.key});
          if (res.status === 200) {
            await Swal.fire({
              title: "Redefinição de senha!",
              text: res.data,
              icon: "success",
              customClass: {
                confirmButton: "btn btn-success btn-fill",
              },
              showCloseButton: true,
              buttonsStyling: false
            });
            await this.$router.push({path: "/"});
          }
        } catch (e) {
          await Swal.fire({
            title: "Erro ao redefinir a senha!",
            text: e.response.data,
            icon: "error",
            customClass: {
              confirmButton: "btn btn-info btn-fill",
            },
            confirmButtonText: "OK",
            showCloseButton: true,
            buttonsStyling: false
          });
        }
      }
    }
  }
};
</script>
