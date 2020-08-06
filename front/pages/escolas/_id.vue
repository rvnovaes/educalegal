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
            <escola-form :name="school.name"
                         :legal-name="school.legalName"
                         :legal-type="school.legalType"
                         :cnpj="school.cnpj"
                         :phone="school.phone"
                         :site="school.site"
                         :email="school.email"
                         :zip="school.zip"
                         :street="school.street"
                         :streetNumber="school.streetNumber"
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
  import gql from 'graphql-tag'

  export const SCHOOL = gql`
    query school($id: Int!) {
        school(id: $id) {
        id,
        name,
        legalName,
        legalType,
        cnpj,
        phone,
        site,
        email,
        zip,
        street,
        streetNumber,
        unit,
        neighborhood,
        city,
        state
    }
  }`

  export default {
    name: 'escola-edicao',
    layout: 'DashboardLayout',
    components: {
      EscolaForm,
    },
    data() {
      return {
        school: '',
      }
    },
    apollo: {
      school:{
        query: SCHOOL,
        variables () {
          return {
            id: this.$route.params.id
          }
        },
        loadingKey: 'carregando...',
        // update: data => data.school
      }
    }
  }
</script>
