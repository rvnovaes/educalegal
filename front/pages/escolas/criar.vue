<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-11">
          <h6 class="h2 text-white d-inline-block mb-0">{{$route.name}}</h6>
        </div>
        <div class="col-1 text-right">
          <base-button size="sm" type="neutral" @click="tour">Ajuda</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <div class="card-wrapper">
            <criar-escola-form>
            </criar-escola-form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CriarEscolaForm from '@/components/pages/forms/CriarEscolaForm'

export default {
  name: 'escola-criar',
  layout: 'DashboardLayout',
  components: {
    CriarEscolaForm,
  },
}
</script>
