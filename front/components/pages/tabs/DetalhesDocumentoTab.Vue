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

      <tab-pane id="envelope" v-if="currentDocument.envelope">
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

      <tab-pane id="destinatarios" v-if="currentDocument.envelope">
         <span slot="title">
           <i class="fa fa-user"></i> Destinatários
          </span>
        <div class="card-deck">
          <card v-for="signer in currentDocument.signers"
                :key="signer.id"
                :headerClasses="['text-white', 'rounded-bottom', cardType(signer.status)]"
          >
            <span slot="header"> {{ signer.status | capitalize }} </span>


            <ul class="list-group list-group-flush">
              <li class="list-group-item card-title"><span class="font-weight-bold">Nome: </span>{{ signer.name }}</li>
              <li class="list-group-item"><span class="font-weight-bold">E-mail: </span>{{ signer.email }}</li>
              <li class="list-group-item"><span class="font-weight-bold">Data de Criação: </span>{{
                  signer.created_date
                }}
              </li>
              <li class="list-group-item"><span class="font-weight-bold">Data do Envio: </span>{{ signer.sent_date }}
              </li>
              <li class="list-group-item"><span class="font-weight-bold">Tipo: </span>{{ signer.type }}</li>
              <li v-if="signer.pdf_filenames" class="list-group-item">
                <p class="card-text">PDFs: {{ signer.pdf_filenames|linebreaks }}</p>
              </li>
            </ul>

          </card>
        </div>
      </tab-pane>

    </tabs>
    <!--  TODO Testar bloqueio de CORS para download em ambiente real. Em localhost ele bloqueia  -->
    <base-button @click="downloadDocument(currentDocument.ged_link, currentDocument.name)" type="primary"><i
      class="ni ni-cloud-download-95"></i>Baixar
    </base-button>
    <base-button @click="back()" type="warning"><i class="ni ni-bold-left"></i>Voltar</base-button>

  </div>


</template>

<script>
import Swal from "sweetalert2";

export default {
  name: "detalhes-document-tab",
  props: ["currentDocument"],
  components: {},
  data() {
    return {};
  },
  methods: {
    cardType(status) {
      if (status === "criado") {
        return "el-bg-primary";
      }
      if (status === "enviado") {
        return "el-bg-info";
      }
      if (status === "entregue") {
        return "el-bg-warning";
      }
      if (status === "finalizado") {
        return "el-bg-success";
      }
      if (status === "recusado" || status === "inválido") {
        return "el-bg-danger";
      }

    },
    back() {
      this.$router.push({
        path: "/arquivo"
      });
    },
    async downloadDocument(ged_link, documentName) {
      try {
        const res = await this.$axios.get(ged_link, {responseType: "blob"});
        const blob = new Blob([res.data], {type: "application/pdf"});
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = documentName;
        link.click();
        URL.revokeObjectURL(link.href);
      } catch (e) {
        await Swal.fire({
          title: `Erro ao baixar ${documentName}`,
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


<style>
.card {
  padding-left: 20px;
  padding-right: 20px;
}

.card-deck {
  margin-top: 25px;
}

.el-bg-primary {
  background-color: #5e72e4;
  margin-top: 15px;
}

.el-bg-info {
  background-color: #11cdef;
  margin-top: 15px;
}

.el-bg-warning {
  background-color: #fb6340;
  margin-top: 15px;
}

.el-bg-success {
  background-color: #2dce89;
  margin-top: 15px;
}

.el-bg-danger {
  background-color: #f5365c;
  margin-top: 15px;
}


</style>
