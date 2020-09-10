import Fuse from "fuse.js";

export default {
  computed: {
    /***
     * Returns a page from the searched data or the whole data. Search is performed in the watch section below
     */
    queriedData() {
      let result = this.tableData;
      if (this.searchedData.length > 0) {
        result = this.searchedData;
      } else {
        if (this.searchQuery) {
          result = [];
        }
      }
      return result;
    },
  },
  data() {
    return {
      searchQuery: "",
      searchedData: [],
      fuseSearch: null
    };
  },
  methods: {
    refreshFuseSearch() {
      this.fuseSearch = new Fuse(this.tableData, {
        keys: ["name", "description"],
        // At what point does the match algorithm give up. A threshold of 0.0 requires a perfect match
        //   (of both letters and location), a threshold of 1.0 would match anything.
        // https://fusejs.io/concepts/scoring-theory.html#scoring-theory
        // ignoreLocation não funcionou...
        threshold: 0.4,
        distance: 2000
      });
    }

  },
  mounted() {
    this.refreshFuseSearch();
  },
  watch: {
    /**
     * Searches through the table data by a given query.
     * NOTE: If you have a lot of data, it's recommended to do the search on the Server Side and only display the results here.
     * @param value of the query
     */
    searchQuery(value) {
      let result = this.tableData;
      if (value !== "") {
        result = this.fuseSearch.search(this.searchQuery);
      }
      this.searchedData = result;
    },
    // Como o carregamento de dados para tableData e assincrono, toda vez que for alterado esse valor  (eg page refresh)
    // o FUSE deve ser novamente gerado, senao a busca nao funciona.
    tableData() {
      this.refreshFuseSearch();
    }
  }
};
