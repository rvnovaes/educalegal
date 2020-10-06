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
            <span class="font-weight-bold">Data de criação: </span>{{ currentDocument.created_date | formatDateTime}}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data de alteração: </span>{{ currentDocument.altered_date | formatDateTime}}
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
          <li v-if="currentDocument.related_documents" class="list-group-item">
            <span class="font-weight-bold">Documentos Relacionados:</span>
            <ul v-for="related_document in currentDocument.related_documents">
              <li><a v-bind:href="'/arquivo/' + related_document.doc_uuid">{{ related_document.name }}</a></li>
            </ul>
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
            <span class="font-weight-bold">Data de Criação: </span>{{ currentDocument.envelope.envelope_created_date | formatDateTime}}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data de Alteração: </span>{{ currentDocument.envelope.status_update_date | formatDateTime}}
          </li>
          <li class="list-group-item">
            <span class="font-weight-bold">Data do Envio: </span>{{ currentDocument.envelope.sent_date | formatDateTime}}
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
                :headerClasses="['text-white', 'rounded-bottom', cardType(signer.status)]">
            <span slot="header"> {{ signer.status | capitalize }} </span>

            <ul class="list-group list-group-flush">
              <li class="list-group-item card-title"><span class="font-weight-bold">Nome: </span>{{ signer.name }}</li>
              <li class="list-group-item"><span class="font-weight-bold">E-mail: </span>{{ signer.email }}</li>
              <li class="list-group-item"><span class="font-weight-bold">Data de Criação: </span>{{ signer.created_date | formatDateTime}}
              </li>
              <li class="list-group-item"><span class="font-weight-bold">Data do Envio: </span>{{ signer.sent_date | formatDateTime}}
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

    <div v-if="currentDocument.status !== 'rascunho'" class="row justify-content-center align-items-center">
      <div v-if="currentDocument.parent == null">
        <!--  TODO Testar bloqueio de CORS para download em ambiente real. Em localhost ele bloqueia  -->
        <!-- pdf -->
        <base-button v-if="currentDocument.cloud_file" @click="downloadDocument(currentDocument.doc_uuid,
        currentDocument.name, 'pdf')" type="danger"><i class="ni ni-cloud-download-95"></i>PDF
        </base-button>
        <base-button v-else-if=currentDocument.ged_link @click="downloadDocument(currentDocument.ged_link,
        currentDocument.name, 'pdf')" type="danger"><i class="ni ni-cloud-download-95"></i>PDF
        </base-button>
        <!-- docx -->
        <base-button v-if="currentDocument.docx_file" @click="downloadDocument(currentDocument.docx_file.doc_uuid,
        currentDocument.docx_file.name, 'docx')" type="primary"><i class="ni ni-cloud-download-95"></i>Word
        </base-button>

        <!-- assinatura eletronica -->
        <base-button v-if="currentDocument.submit_to_esignature === false"
                     @click="send_to_esignature(currentDocument.doc_uuid)"
                     :type="esignatureButtonType"><i class="ni ni-sound-wave"></i>Enviar para assinatura
        </base-button>

        <!-- email -->
        <base-button @click="send_email(currentDocument.doc_uuid)" :type="emailButtonType"><i class="ni ni-email-83"
        ></i>Enviar por e-mail
        </base-button>
      </div>
      <div v-if="currentDocument.parent">
        <!-- pdf -->
        <base-button v-if="currentDocument.cloud_file" @click="downloadDocument(currentDocument.doc_uuid,
        currentDocument.name, 'pdf')" type="info"><i class="ni ni-cloud-download-95"></i>Download
        </base-button>
        <base-button v-else-if=currentDocument.ged_link @click="downloadDocument(currentDocument.ged_link,
        currentDocument.name, 'pdf')" type="info"><i class="ni ni-cloud-download-95"></i>Download
        </base-button>
      </div>
    </div>
  </div>


</template>

<script>
import Swal from "sweetalert2";

export default {
  name: "detalhes-document-tab",
  props: ["currentDocument"],
  components: {},
  data() {
    return {
      emailButtonType: "success",
      esignatureButtonType: "success"
    };
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
    async send_email(doc_uuid) {
      this.emailButtonType = "secondary";
      try {
        const res = await this.$axios.post("/v2/documents/send_email/", {doc_uuid: doc_uuid});
        if (res.status === 202) {
          this.emailButtonType = "success";
          await Swal.fire({
            title: "O e-mail foi enviado com sucesso!",
            html: res.data,
            icon: "success",
            showCloseButton: true,
            customClass: {
              confirmButton: "btn btn-success btn-fill",
            },
          });
        }
      } catch (e) {
        let errorMessage = ''
        if (e.response.data){
          errorMessage = e.response.data
        }
        else {
          errorMessage = e
        }
        this.emailButtonType = "success";
        await Swal.fire({
          title: "Houve erro ao enviar o e-mail.",
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
    },
    async send_to_esignature(doc_uuid) {
      this.esignatureButtonType = "secondary";
      try {
        const res = await this.$axios.post("/v2/documents/send_to_esignature/", {doc_uuid: doc_uuid});
        // o docusign retorna 201 e o clicksign retorna 202
        if (res.status === 201 || res.status === 202) {
          this.esignatureButtonType = "success";
          await Swal.fire({
            title: "O documento foi enviado para a assinatura eletrônica com sucesso!",
            html: res.data,
            icon: "success",
            showCloseButton: true,
            customClass: {
              confirmButton: "btn btn-success btn-fill",
            },
          });
        }
      } catch (e) {
        let errorMessage = ''
        if (e.response.data){
          errorMessage = e.response.data
        }
        else {
          errorMessage = e
        }
        this.esignatureButtonType = "success";
        await Swal.fire({
          title: "Houve erro ao enviar para a assinatura eletrônica.",
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
    },
    async downloadDocument(doc_uuid, documentName, fileKind) {
      try {
        const url = "/v2/documents/" + doc_uuid + "/cloud_download/";
        const res = await this.$axios.get(url, {responseType: "blob"});
        let blob = undefined;
        if (fileKind === "pdf") {
          blob = new Blob([res.data], {type: "application/pdf"});
        } else {
          blob = new Blob([res.data], {type: "application/msword"});
        }
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
          showCloseButton: true,
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
