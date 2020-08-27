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
      <base-dropdown menu-on-right
                     class="nav-item"
                     tag="li"
                     title-tag="a"
                     title-classes="nav-link pr-0">
        <a href="#" class="nav-link pr-0" @click.prevent slot="title-container">
                    <div class="media align-items-center">
          <div class="media-body ml-2 d-none d-lg-block">
            <span class="mb-0 text-sm  font-weight-bold">{{ fullName }}</span>
          </div>
          </div>
        </a>

        <template>

          <div class="dropdown-header noti-title">
            <h6 class="text-overflow m-0">Welcome!</h6>
          </div>
          <a href="#!" class="dropdown-item">
            <i class="ni ni-single-02"></i>
            <span>My profile</span>
          </a>
          <a href="#!" class="dropdown-item">
            <i class="ni ni-settings-gear-65"></i>
            <span>Settings</span>
          </a>
          <a href="#!" class="dropdown-item">
            <i class="ni ni-calendar-grid-58"></i>
            <span>Activity</span>
          </a>
          <a href="#!" class="dropdown-item">
            <i class="ni ni-support-16"></i>
            <span>Support</span>
          </a>
          <div class="dropdown-divider"></div>
          <!--          <a href="#!" class="dropdown-item">-->
          <nuxt-link @click.native="onLogout" class="dropdown-item" to="/">
            <i class="ni ni-user-run"></i>
            <span>Sair</span>
          </nuxt-link>
          <!--          </a>-->

        </template>
      </base-dropdown>
    </ul>
  </base-nav>
</template>
<script>
import {CollapseTransition} from "vue2-transitions";
import {mapState} from "vuex";
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
      this.$auth.logout();
      // Certifique-se que sai da aplicacao. TODO: Pq o redirect do nuxt auth não funciona?
      this.$router.push({path: "/"});
    },
  }
};
</script>
