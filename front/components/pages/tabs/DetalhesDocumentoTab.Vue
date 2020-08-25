<template>
  <div>
    <tabs tabNavClasses="nav-fill flex-column flex-sm-row nav-wrapper"
          tabContentClasses="card shadow">
      <tab-pane id="documento">
        <span slot="title">
          <i class="fa fa-file"></i> Documento
        </span>
        <ul class="list-group list-group-flush">
          <li class="list-group-item">
            <span class="font-weight-bold">Nome do arquivo: </span>{{ currentDocument.name }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data de criação: </span>{{ currentDocument.created_date }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data de alteração: </span>{{ currentDocument.altered_date }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Status: </span>{{ currentDocument.status }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Descrição: </span>{{ currentDocument.description }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Doc UUID: </span>{{ currentDocument.doc_uuid }}
          </li>
        </ul>

      </tab-pane>

      <tab-pane id="envelope">
        <span slot="title">
          <i class="fa fa-envelope-open"></i> Envelope
        </span>
        <ul class="list-group list-group-flush">
          <li class="list-group-item">
            <span class="font-weight-bold">ID: </span>{{ currentDocument.envelope.identifier }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Provedor: </span>{{ currentDocument.envelope.signing_provider }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data de Criação: </span>{{ currentDocument.envelope.envelope_created_date }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data de Alteração: </span>{{ currentDocument.envelope.status_update_date }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data do Envio: </span>{{ currentDocument.envelope.sent_date }}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Status: </span>{{ currentDocument.envelope.status }}
          </li>
        </ul>
      </tab-pane>

      <tab-pane id="destinatarios">
         <span slot="title">
           <i class="fa fa-user"></i> Destinatários
          </span>
        <div class="card-deck">
          <card v-for="signer in currentDocument.signers" :key="signer.id">
            <div class="card-header">{{ signer.status | capitalize }} </div>
            <ul class="list-group list-group-flush">
              <li class="list-group-item card-title">{{ signer.name }}</li>
              <li class="list-group-item">Dapibus ac facilisis in</li>
              <li class="list-group-item">Vestibulum at eros</li>
            </ul>

          </card>
        </div>
      </tab-pane>

    </tabs>
    <base-button @click="back()" type="warning"><i class="ni ni-bold-left"></i>Voltar</base-button>

  </div>




</template>

<script>
export default {
  name: "detalhes-document-tab",
  props: ["currentDocument"],
  components:{
  },
  methods: {
    back() {
      this.$router.push({
        path: "/arquivo"
      });
    }
  }
}
</script>


<style>
.card{
  padding-left: 20px;
  padding-right: 20px;
}

.card-deck {
  margin-top: 25px;
}
</style>
