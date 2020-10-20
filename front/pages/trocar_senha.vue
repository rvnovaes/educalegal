<template>
  <div>
    <!-- Header -->
    <div class="header bg-gradient-secondary py-7 py-lg-8 pt-lg-9">
      <div class="container">
        <div class="header-body text-center mb-5">
          <div class="row justify-content-center">
            <div class="col-xl-5 col-lg-6 col-md-8 px-5">
              <img src="static/img/brand/logo_educa_legal.png" alt="Logo Educa Legal">
              <p class="text-lead">A sua senha deve ser redefinida</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Page content -->
    <div class="container mt--8 pb-5">
      <!-- Table -->
      <div class="row justify-content-center">
        <div class="col-lg-6 col-md-8">
          <div class="card bg-secondary border-0">
            <div class="card-header bg-transparent pb-3">
              <div class="text-center text-lg">Redefina a sua senha</div>
            </div>
            <div class="card-body px-lg-5 py-lg-5">
              <div class="text-center text-muted mb-4">
                <small>Preencha os campos abaixo:</small>
              </div>
              <validation-observer v-slot="{handleSubmit}" ref="formValidator">
                <form role="form" @submit.prevent="handleSubmit(onSubmit)">
                  <base-input alternative
                              class="mb-3"
                              name="Senha Atual"
                              :rules="{required: true, min: 6}"
                              prepend-icon="ni ni-lock-circle-open"
                              type="password"
                              placeholder="Senha Atual"
                              v-model="old_password">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              name="Nova Senha"
                              :rules="{required: true, min: 6}"
                              prepend-icon="ni ni-lock-circle-open"
                              type="password"
                              placeholder="Nova Senha"
                              v-model="new_password1">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              name="Confirmar Nova Senha"
                              :rules="{required: true, min: 6}"
                              prepend-icon="ni ni-lock-circle-open"
                              type="password"
                              placeholder="Confirmar Nova Senha"
                              v-model="new_password2">
                  </base-input>

                  <div class="text-center">
                    <button type="submit" class="btn btn-primary mt-4">Redefinir Senha</button>
                  </div>
                </form>
              </validation-observer>
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
  name: "trocar-senha",
  auth: false,
  data() {
    return {
      old_password: "",
      new_password1: "",
      new_password2: "",
    };
  },
  methods: {
    async onSubmit() {
      try {
        const payload = {
          "old_password": this.old_password,
          "new_password1": this.new_password1,
          "new_password2": this.new_password2,
        };
        const res = await this.$axios.put("/v2/change-password/", payload);
        if (res.status === 200) {
          this.close();
          await Swal.fire({
            title: `A senha foi alterada com sucesso!`,
            buttonsStyling: false,
            icon: "success",
            showCloseButton: true,
            customClass: {
              confirmButton: "btn btn-success btn-fill",
            }
          });
          await this.$auth.logout();
          await this.$router.push({path: "/"});
        }
      } catch (e) {
        let errorMessage = ''
        if (e.response.data){
          errorMessage = e.response.data
        }
        else {
          errorMessage = e.toString()
        }
        await Swal.fire({
          title: "Erro ao alterar a senha",
          text: errorMessage,
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
};
</script>
<style></style>
