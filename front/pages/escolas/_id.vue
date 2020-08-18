<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-lg-6 col-7">
          <h6 class="h2 text-white d-inline-block mb-0">{{$route.name}}</h6>
          <nav aria-label="breadcrumb" class="d-none d-md-inline-block ml-md-4">
            <route-breadcrumb/>
          </nav>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <div class="card-wrapper">
            <escola-form :id="school.id"
                         :name="school.name"
                         :legal_name="school.legal_name"
                         :legal_nature="school.legal_nature"
                         :cnpj="school.cnpj"
                         :phone="school.phone"
                         :site="school.site"
                         :email="school.email"
                         :zip="school.zip"
                         :street="school.street"
                         :street_number="school.street_number"
                         :unit="school.unit"
                         :neighborhood="school.neighborhood"
                         :city="school.city"
                         :state="school.state">
            </escola-form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
  import EscolaForm from '@/components/pages/forms/EscolaForm'

  export default {
    name: 'escola-edicao',
    layout: 'DashboardLayout',
    components: {
      EscolaForm,
    },
    data() {
      return {
        id: this.$route.params.id
      }
    },
    computed: {
      school () {
        // return this.$store.state.schools.schools.find(school => school.id === Number(this.id))
        // return this.$store.getters.schools.getSchool(Number(this.id))
        return this.$store.getters["schools/getSchool"](this.id)
      }
    }
  }
</script>
