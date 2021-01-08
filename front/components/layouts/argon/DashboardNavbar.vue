<template>
  <base-nav
    container-classes="container-fluid"
    class="navbar-top border-bottom navbar-expand"
    :class="{'bg-primary navbar-dark': type === 'default'}"
    :type="navBarType">
    <div class="text-white font-weight-bold">
      <slot name="brand">{{ tenant }} <div v-if="navBarType === 'danger'">SUPER USUÁRIO</div></slot>
    </div>
    <ul class="navbar-nav align-items-center ml-auto ml-md-10">

      <li class="nav-item d-xl-none">
        <!-- Sidenav toggler -->
        <div class="pr-3 sidenav-toggler"
             :class="{active: $sidebar.showSidebar, 'sidenav-toggler-dark': type === 'default', 'sidenav-toggler-light': type === 'light'}"
             @click="toggleSidebar">
          <div class="sidenav-toggler-inner">
            <i class="sidenav-toggler-line"></i>
            <i class="sidenav-toggler-line"></i>
            <i class="sidenav-toggler-line"></i>
          </div>
        </div>
      </li>
      <base-dropdown menu-on-right
                     class="nav-item"
                     tag="li"
                     title-tag="a"
                     title-classes="nav-link pr-0">
        <a href="#" class="nav-link pr-0" @click.prevent slot="title-container">
          <div class="media align-items-center">
            <span class="mb-0 text-sm  font-weight-bold">{{ fullName }}</span>
          </div>
        </a>
        <template>
          <div class="dropdown-header noti-title">
            <h6 class="text-overflow m-0">Bem-vindo!</h6>
          </div>
          <a href="/plano" class="dropdown-item">
            <i class="ni ni-settings-gear-65"></i>
            <span>Dados do Plano</span>
          </a>
          <div class="dropdown-divider"></div>
          <nuxt-link @click.native="onLogout" class="dropdown-item" to="/">
            <i class="ni ni-user-run"></i>
            <span>Sair</span>
          </nuxt-link>
        </template>
      </base-dropdown>
    </ul>
  </base-nav>
</template>
<script>
import {CollapseTransition} from "vue2-transitions";
import BaseNav from "@/components/argon-core/Navbar/BaseNav.vue";
import Modal from "@/components/argon-core/Modal.vue";

export default {
  components: {
    CollapseTransition,
    BaseNav,
    Modal
  },
  props: {
    type: {
      type: String,
      default: "default", // default|light
      description: "Look of the dashboard navbar. Default (Green) or light (gray)"
    }
  },
  computed: {
    routeName() {
      const {name} = this.$route;
      return this.capitalizeFirstLetter(name);
    },

    fullName: function () {
      return this.$auth.user.first_name + " " + this.$auth.user.last_name;
    },
    tenant: function () {
      return this.$auth.user.tenant_name;
    },
    navBarType: function () {
      if (this.$auth.user.is_superuser){
        return "danger"
      }
      else {
        return "primary"
      }
    }

  },
  data() {
    return {
      activeNotifications: false,
      showMenu: false,
      searchModalVisible: false,
      searchQuery: ""
    };
  },
  methods: {
    capitalizeFirstLetter(string) {
      return string.charAt(0).toUpperCase() + string.slice(1);
    },
    toggleNotificationDropDown() {
      this.activeNotifications = !this.activeNotifications;
    },
    closeDropDown() {
      this.activeNotifications = false;
    },
    toggleSidebar() {
      this.$sidebar.displaySidebar(!this.$sidebar.showSidebar);
    },
    hideSidebar() {
      this.$sidebar.displaySidebar(false);
    },
    onLogout() {
      // Limpa todos os estados do VUEX
      // https://tahazsh.com/vuebyte-reset-module-state
      this.$store.dispatch("dashboard/resetState");
      this.$store.dispatch("documents/resetState");
      this.$store.dispatch("interviews/resetState");
      this.$store.dispatch("schools/resetState");
      this.$store.dispatch("tenant/resetState");
      this.$auth.logout();

      // Certifique-se que sai da aplicacao. TODO: Pq o redirect do nuxt auth não funciona?
      this.$router.push({path: "/"});
    },
  }
};
</script>
