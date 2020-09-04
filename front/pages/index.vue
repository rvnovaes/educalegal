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
                <small>Digite seu e-mail e sua senha</small>
              </div>
              <validation-observer v-slot="{handleSubmit}" ref="formValidator">
                <form role="form" @submit.prevent="handleSubmit(onSubmit)">
                  <base-input alternative
                              class="mb-3"
                              name="Email"
                              :rules="{required: true, email: true}"
                              prepend-icon="ni ni-email-83"
                              placeholder="Email"
                              v-model="credentials.username">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              name="Senha"
                              :rules="{required: true, min: 6}"
                              prepend-icon="ni ni-lock-circle-open"
                              type="password"
                              placeholder="Senha"
                              v-model="credentials.password">
                  </base-input>

<!--                  <base-checkbox v-model="rememberMe">Lembrar</base-checkbox>-->
                  <div class="text-center">
                    <base-button type="primary" native-type="submit" class="my-4">Entrar</base-button>
                  </div>
                </form>
              </validation-observer>
            </div>
          </div>
          <div class="row mt-3">
            <div class="col-6">
              <n-link to="/recuperar" class="text-light"><small>Esqueceu a senha?</small></n-link>
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
    layout: 'AuthLayout',
    data() {
      return {
        credentials: {
          // passamos o email em username uma vez que a API do EL espera um post com username e password
          // Entretanto, aceita tanto o username quanto email nesse campo
          username: '',
          password: '',
        },
        // rememberMe: false,
      };
    },
    methods: {
      async onSubmit() {
        const credentials = this.credentials
        try {
          await this.$auth.loginWith('local', { data: credentials })
          // await this.$auth.loginWith('customScheme', { data: credentials })
          await Swal.fire({
            title: "Bem-vindo ao Educa Legal!",
            buttonsStyling: false,
            icon: "success",
            timer: 3000,
            customClass: {
              confirmButton: "btn btn-success btn-fill",
            }
          })
          } catch (e) {
          await Swal.fire({
            title: "Usuário ou senha inválidos!",
            text: e,
            icon: "error",
            customClass: {
              confirmButton: "btn btn-info btn-fill",
            },
            confirmButtonText: "OK",
            buttonsStyling: false
          });
        }
      }
    }
  };
</script>
