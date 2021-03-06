export default {
  methods: {
    tour() {
      this.$tours["pageTour"].start();
    }
  },
  data() {
    return {
      tourOptions: {
        useKeyboardNavigation: true,
        labels: {
          buttonSkip: "Dispensar",
          buttonPrevious: "Anterior",
          buttonNext: "Próximo",
          buttonStop: "Fim"
        }
      },
      // Painel - /painel
      painelSteps: [
        {
          target: ".painel",
          header: {
            title: "Painel",
          },
          params: {
            placement: "right"
          },
          content: `No painel você acessa informações gerais sobre o uso do Educa Legal. Você também pode usar as setas para navegar entre as dicas e ESC para fechar.`
        },
        {
          target: ".documentos-gerados",
          header: {
            title: "Documentos gerados",
          },
          params: {
            placement: "right"
          },
          content: `Aqui você vê quantos documentos sua escola criou no mês.`
        },
        {
          target: ".documentos-gerados-mes-anterior",
          content: `Você compara também com os documentos gerados no mês anterior.`
        },
        {
          target: ".documentos-andamento",
          header: {
            title: "Documentos em andamento",
          },
          content: `São os documentos que ainda estão sendo preenchidos.`
        },
        {
          target: ".assinaturas",
          header: {
            title: "Assinaturas eletrônicas",
          },
          content: `Aqui você vê quantos documentos sua escola enviou para assinatura eletrônica.`
        },
        {
          target: ".assinaturas-andamento",
          header: {
            title: "Assinaturas em andamento",
          },
          content: `Representam os documentos que foram enviados para os destinatários mais ainda não contam com a assinatura de todos. Lembre-se que você pode voltar à ajuda a qualquer momento.`
        }
      ],
      // Criar documentos - criar/index
      criarDocumentosSteps: [
        {
          target: ".criar",
          header: {
            title: "Criar documentos",
          },
          content: `Nesta página você tem acesso a todos os modelos de documentos disponibilizados para sua escola. Você também pode usar as setas para navegar entre as dicas e ESC para fechar.`,
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
          content: `Clique nesse botão para criar um novo documento com base neste modelo.  Lembre-se que você pode voltar à ajuda a qualquer momento.`,
          params: {
            placement: "top",
            highlight: false,
            enableScrolling: false
          }
        },
      ],

      // Arquivo - / arquivo/index

      arquivoSteps: [
        {
          target: ".arquivo",
          header: {
            title: "Arquivo",
          },
          content: `No arquivo você acessa e pesquisa todos os documentos já gerados por sua escola. Continue o tour para conhecer os filtros que você pode utilizar. Pode ser usada uma combinação de vários filtros. Após definir os filtros, clique no botão buscar. Se quiser limpar os filtros definidos e começar tudo de novo, clique em limpar.`,
          params: {
            placement: "right",
            enableScrolling: false
          }
        },
        //Aqui tivemos que usar o target como classe, pq so conseguimos passar para a coluna (que e outro componente) a classe
        {
          target: ".filtro-data",
          content: `Aqui você filtra por data de criação do documento. Você pode selecionar um período clicando em duas datas distintas ou apenas em um dia, clicando duas vezes no mesmo dia. Após definir os filtros, clique no botão buscar para recuperar os documentos de acordo com os critérios informados.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".filtro-modelo",
          content: `Você pode filtrar por um ou vários modelos de documentos ao mesmo tempo. Lembre-se que os filtros são cumulativos, ou seja, você pode filtrar por data E modelo E escola E status ao mesmo tempo.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".filtro-escola",
          content: `Você pode filtrar por uma ou mais escolas ao mesmo tempo. Lembre-se que sempre que houver alteração dos filtros você deve clicar em buscar para aplicá-los.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".filtro-status",
          content: `Filtra os documentos por status. O primeiro status do documento é "criado". Depois disso, pode ser enviado para o GED, enviado por e-mail ou ainda para assinatura eletrônica.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".paginacao",
          content: `Defina quantos documentos você quer exibir ao mesmo tempo na página. No rodapé da página você consegue ver o número de documentos recuperados de acordo com os critérios de filtro e pode navegar entre as páginas.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".botao-buscar",
          content: `Após definir os filtros, clique nesse botão para aplicá-los e recuperar os documentos de acordo com os critérios fornecidos. Se não tiver informado nenhum filtro, todos os documentos serão recuperdados.`,
          params: {
            placement: "left",
            enableScrolling: false
          }
        },
        {
          target: ".botao-limpar",
          content: `Esse botão limpa todos os filtros informados e busca todos os documentos.`,
          params: {
            placement: "bottom",
            enableScrolling: false
          }
        },
        {
          target: ".criacao-documento",
          content: `Essa é a data na qual o documento foi criado na plataforma.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".nome-documento",
          content: `Essa é o nome do arquivo do documento criado.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".modelo-documento",
          content: `Esse é o modelo do documento criado.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-documento",
          content: `Nome da escola que consta do documento gerado.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".status-documento",
          content: `Status atual do documento.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".alteracao-documento",
          content: `Data da última alteração de status do documento.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".total-documentos",
          content: `Aqui você vê quantos documentos foram recuperados de acordo com os filtros que você definiu.`,
          params: {
            placement: "top",
            enableScrolling: true
          }
        },

        {
          target: ".pagination-no-border",
          content: `Estes números e setas permitem navegar entre as páginas de documentos recuperados.`,
          params: {
            placement: "top",
            enableScrolling: true
          }
        },
        {
          target: ".edit",
          content: `Clique neste botão para ver os detalhes e baixar o documento. Lembre-se que você pode voltar à ajuda a qualquer momento.`,
          params: {
            placement: "left",
            enableScrolling: true
          }
        },
      ],
      // Escolas - / escolas/index
      escolaSteps: [
        {
          target: ".escolas",
          header: {
            title: "Escolas",
          },
          content: `Todos os documentos e contratos gerados se referem à uma escola. Dados tais como razão social, CNPJ, endereço, e-mail, entre outros, são cadastrados aqui e são automaticamente usados no preenchimento dos contratos.`,
          params: {
            placement: "right",
            enableScrolling: false
          }
        },
        {
          target: ".escola-nome",
          content: `Nome de fantasia da escola. Você pode clicar no título desta coluna para alterar a ordenação por nome da escola.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-telefone",
          content: `Telefone principal da escola que será usado no preenchimento dos documentos.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-email",
          content: `E-mail da escola. O cadastro correto deste e-mail é fundamental. Por padrão, os documentos enviados por e-mail ou para assinatura eletrônica usam o endereço cadastrado neste campo.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-site",
          content: `Endereço do site da escola. Ex.: https://minhaescola.com.br`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-cidade",
          content: `Cidade da escola. Lembre-se que, ao clicar no título de qualquer coluna, você altera a ordenação.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-estado",
          content: `UF da escola.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".botao-nova-escola",
          header: {
            title: "Nova escola",
          },
          content: `Todos os documentos e contratos gerados se referem à uma escola. Dados tais como razão social, CNPJ, endereço, e-mail, entre outros, são cadastrados aqui. Você pode cadastrar quantas escolas quiser.`,
          params: {
            placement: "left",
            enableScrolling: false
          }
        },
        {
          target: ".botao-editar-escola",
          content: `Aqui você pode editar os dados de uma escola já cadastrada.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".botao-apagar-escola",
          content: `Você pode apagar uma escola apenas se ainda não houver criado nenhum documento para ela. Uma vez criados documentos, a escola fica cadastrada permanentemente. Lembre-se que você pode voltar à ajuda a qualquer momento.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
      ],
      // Escolas Form - /escolas/criar e /escolas/n onde n é o id da escola
      escolaDetalhesSteps: [
        {
          target: ".escola-nome",
          content: `Nome fantasia da escola. Este nome é uma identificação usada no sistema e não é utilizada no preenchimento dos contratos e documentos`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-razao",
          content: `A razão social deve ser exatamente como inscrita no cadastro do CNPJ. Ela será usada no preenchimento de contratos e documentos`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-cnpj",
          content: `CNPJ da escola. Caso se trate de pessoa física, inserir o CPF.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".escola-email",
          content: `E-mail da escola. O cadastro correto deste e-mail é fundamental. Por padrão, os documentos enviados por e-mail ou para assinatura eletrônica usam o endereço cadastrado neste campo.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".salvar-escola",
          content: `Clique nesse botão para salvar as alterações ou em Voltar para descartar.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
        {
          target: ".voltar",
          content: `Clique nesse botão para descartar as alterações e voltar para lista de escolas. Lembre-se que você pode voltar à ajuda a qualquer momento.`,
          params: {
            placement: "top",
            enableScrolling: false
          }
        },
      ]
    };
  }
};
