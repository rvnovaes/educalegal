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
        <div class="col-lg-6 col-5 text-right">
          <base-button size="sm" type="neutral">New</base-button>
          <base-button size="sm" type="neutral">Filters</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <div class="card-wrapper">
            <escola-form :name="school.name"
                         :legal-name="school.legalName"
                         :city="school.city"
                         :state="school.state"
                         :zip="school.zip">
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
    query school($id: Int!)
            {
            school(id: $id) {
              id,
              name,
              legalName,
              city,
              state,
              zip
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
