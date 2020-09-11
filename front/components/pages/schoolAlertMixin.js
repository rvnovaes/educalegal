import Swal from "sweetalert2";

export default {
  mounted() {
    const schoolsCount = this.$auth.user.schools_count;
      if (schoolsCount === 0) {
        Swal.fire({
          title: "Bem-vindo ao Educa Legal!",
          text: "Para começar a usar a plataforma, você deve cadastrar sua primeira escola. Os dados da escola cadastrada serão usados na geração dos contratos e documentos.",
          icon: "success",
          customClass: {
            confirmButton: "btn btn-success btn-fill",
          },
          confirmButtonText: "Entendido. Leve-me leve até lá!",
          buttonsStyling: false
        });
        this.$router.push({path: "/escolas/criar"});
      }
    }
};
