<template>
  <div>
    <!-- Header -->
    <div class="header bg-gradient-secondary py-7 py-lg-8 pt-lg-9">
      <div class="container">
        <div class="header-body text-center mb-5">
          <div class="row justify-content-center">
            <div class="col-xl-5 col-lg-6 col-md-8 px-5">
              <img src="img/brand/logo_educa_legal.png" alt="Logo Educa Legal">
              <p class="text-lead">Cadastre sua escola e comece a usar agora!</p>
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
              <div class="text-center text-lg">Crie sua conta gratuitamente</div>
            </div>
            <div class="card-body px-lg-5 py-lg-5">
              <div class="text-center text-muted mb-4">
                <small>Preencha os campos abaixo:</small>
              </div>
              <validation-observer v-slot="{handleSubmit}" ref="formValidator">
                <form role="form" @submit.prevent="handleSubmit(onSubmit)">
                  <base-input alternative
                              class="mb-3"
                              prepend-icon="ni ni-circle-08"
                              placeholder="Nome Completo"
                              name="Nome Completo"
                              :rules="{required: true}"
                              v-model="model.fullName">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              prepend-icon="ni ni-hat-3"
                              placeholder="Nome da Escola"
                              name="Nome da Escola"
                              :rules="{required: true}"
                              v-model="model.tenantName">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              prepend-icon="fa fa-phone"
                              placeholder="Telefone"
                              name="Telefone"
                              type="tel"
                              :rules="{required: true}"
                              v-model="model.phone">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              prepend-icon="ni ni-email-83"
                              placeholder="E-mail"
                              name="E-mail"
                              type="email"
                              :rules="{required: true, email: true}"
                              v-model="model.email">
                  </base-input>

                  <base-input alternative
                              class="mb-3"
                              prepend-icon="ni ni-lock-circle-open"
                              placeholder="Senha"
                              type="password"
                              name="senha"
                              :rules="{required: true, min: 6}"
                              v-model="model.password">
                  </base-input>

                  <div class="row my-4">
                    <div class="col-12">
                      <base-input :rules="{ required: { allowFalse: false } }" name="Política de privacidade e termos de uso">
                        <base-checkbox v-model="model.eua">
                          <span class="text-muted">Concordo com a<a
                            href="https://www.educalegal.com.br/politica-de-privacidade/" target="_blank"> política de privacidade e os termos de uso*</a></span>
                        </base-checkbox>
                      </base-input>
                    </div>
                  </div>
                  <div class="text-center">
                    <button type="submit" class="btn btn-primary mt-4">Criar conta</button>
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
  name: "registrar",
  auth: false,
  data() {
    return {
      model: {
        fullName: "",
        tenantName: "",
        phone: "",
        email: "",
        password: "",
        eua: true,
        plan: 1,
        autoEnrolled: true
      }
    };
  },
  methods: {
    async onSubmit() {
      const res = await this.$axios.post("/v2/create_tenant/", {
        full_name: this.model.fullName,
        tenant_name: this.model.tenantName,
        phone: this.model.phone,
        email: this.model.email,
        password: this.model.password,
      });
      if (res.status === 200) {
        await Swal.fire({
          title: `Não foi possível criar sua conta...`,
          text: res.data,
          icon: "warning",
          customClass: {
            confirmButton: "btn btn-info btn-fill",
          },
          confirmButtonText: "OK",
          buttonsStyling: false
        });
      }
      if (res.status === 201) {
        await Swal.fire({
          title: `Você criou ${this.model.tenantName} com sucesso!`,
          buttonsStyling: false,
          icon: "success",
          customClass: {
            confirmButton: "btn btn-success btn-fill",
          }
        });
      await this.$auth.loginWith("local", {
        data:
          {
            username: this.model.email,
            password: this.model.password
          }
      });
      await this.$router.push({path: "/painel"});
      }
    }
  }
};
</script>
<style></style>
