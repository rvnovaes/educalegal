<template>
  <div>
    <base-header class="pb-6">
      <div class="row align-items-center py-4">
        <div class="col-11">
          <h6 class="h2 text-white d-inline-block mb-0 criar">Criar documentos</h6>
          <p class="text-sm text-white font-weight-bold mb-0">
            Os modelos abaixo são usados para gerar novos contratos e documentos
          </p>
        </div>
        <div v-if="loading" class="col-1">
          <HourGlassSpinner></HourGlassSpinner>
        </div>
        <div v-else class="col-1 text-right">
          <base-button size="sm" type="neutral" @click="tour">Ajuda</base-button>
        </div>
      </div>
    </base-header>
    <div class="container-fluid mt--6">
      <div class="row">
        <div class="col">
          <entrevistas-table/>
        </div>
      </div>
    </div>
    <v-tour name="criarTour" :steps="steps" :options="tourOptions"></v-tour>
  </div>
</template>
<script>
import {Table, TableColumn, Option} from "element-ui";
import EntrevistasTable from "@/components/tables/RegularTables/EntrevistasTable";
import HourGlassSpinner from "@/components/widgets/HourGlassSpinner";

export default {
  layout: "DashboardLayout",
  components: {
    EntrevistasTable,
    HourGlassSpinner,
    [Option.name]: Option,
    [Table.name]: Table,
    [TableColumn.name]: TableColumn
  },
  data() {
    return {
      tourOptions: {
        useKeyboardNavigation: true,
        debug: true,
        labels: {
          buttonSkip: "Dispensar",
          buttonPrevious: "Anterior",
          buttonNext: "Próximo",
          buttonStop: "Fim"
        }
      },
      steps: [
        {
          target: ".criar",
          header: {
            title: "Criar documentos",
          },
          content: `Nesta página você tem acesso a todos os modelos de documentos disponibilizados para sua escola.`,
          params: {
            placement: "right",
            enableScrolling: false
          }
        },
        {
          //Aqui tivemos que usar o target como classe, pq so conseguimos passar para a coluna (que e outro componente) a classe
          target: ".busca-modelos",
          content: `Você pode pesquisar o modelo por qualquer palavra no nome ou na descrição. Mesmo que você digite algo errado, nós vamos tentar encontrá-lo para você.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        //Aqui tivemos que usar o target como classe, pq so conseguimos passar para a coluna (que e outro componente) a classe
        {
          target: ".nome-entrevista",
          content: `Esse é o nome pelo qual o modelo de documento ou contrato é identificado na plataforma. Sempre use esse nome ao se referir ao documento. A busca procura por palavras no nome do modelo.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".descricao-entrevista",
          content: `Aqui você encontra informações úteis sobre quando e como usar o modelo. A pesquisa desta página também procura por palavras na descrição. `,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".versao-entrevista",
          content: `Estamos sempre trabalhando em atualizações dos modelos em virtude de novas leis e de melhores práticas jurídicas e de gestão.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".disponibilizacao-entrevista",
          content: `Essa é a data na qual a versão do modelo foi disponibilizada para uso na plataforma.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".edit",
          content: `Clique nesse botão para criar um novo documento com base neste modelo.`,
          params: {
            placement: "top",
            highlight: false,
            enableScrolling: false
          }
        },
      ]
    };
  },
  methods: {
    tour() {
      this.$tours["criarTour"].start();
    }
  },
  computed: {
    loading() {
      return this.$store.state.interviews.loading;
      // return true
    }
  }
};
</script>
<style>
.no-border-card .card-footer {
  border-top: 0;
}
</style>
