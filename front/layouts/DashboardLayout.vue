<template>
  <div class="wrapper">
    <notifications></notifications>
    <side-bar>
      <template slot-scope="props" slot="links">
        <sidebar-item
          :link="{
            name: 'Painel',
            icon: 'ni ni-shop text-primary',
            path: '/painel'
          }">
        </sidebar-item>

        <sidebar-item
          :link="{
            name: 'Criar documentos',
            icon: 'far fa-plus-square text-info',
            path: '/criar'
          }">
        </sidebar-item>

        <!--        <sidebar-item-->
        <!--          :link="{-->
        <!--            name: 'Geração em Lote',-->
        <!--            icon: 'ni ni-ungroup text-orange',-->
        <!--            path: '/lote'-->
        <!--          }">-->
        <!--        </sidebar-item>-->

        <sidebar-item
          :link="{
            name: 'Arquivo',
            icon: 'ni ni-archive-2 text-primary',
            path: '/arquivo'
          }">
        </sidebar-item>

        <sidebar-item
          :link="{
            name: 'Escolas',
            icon: 'ni ni-hat-3 text-green',
            path: '/escolas'
          }">
        </sidebar-item>

        <!--        <sidebar-item-->
        <!--          :link="{-->
        <!--            name: 'Atendimento',-->
        <!--            icon: 'fa fa-user-tie text-red',-->
        <!--            path: '/atendimento'-->
        <!--          }">-->
        <!--        </sidebar-item>-->
      </template>

      <template slot="links-after">
        <hr class="my-3">
        <h6 class="navbar-heading p-0 text-muted">Links Úteis</h6>

        <ul class="navbar-nav mb-md-3">
          <li v-if="gedUrl" class="nav-item">
            <a class="nav-link" :href="gedUrl.url"
               target="_blank" rel="noopener">
              <i class="fa fa-cloud text-primary"></i>
              <span class="nav-link-text">GED</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="https://atendimento.atlassian.net/servicedesk/customer/portal/2"
               target="_blank" rel="noopener">
              <!--              <i class="ni ni-bulb-61"></i>-->
              <i class="fa fa-user-tie text-red"></i>
              <span class="nav-link-text">Atendimento Jurídico</span>
            </a>
          </li>
          <li class="nav-item">
            <a class="nav-link"
               href="https://www.educalegal.com.br"
               target="_blank" rel="noopener">
              <i class="ni ni-chat-round text-warning"></i>
              <span class="nav-link-text">Site Educa Legal</span>
            </a>
          </li>
        </ul>
      </template>
    </side-bar>
    <div class="main-content">
      <dashboard-navbar :type="$route.name === 'alternative' ? 'light': 'default'"></dashboard-navbar>

      <div @click="$sidebar.displaySidebar(false)">
        <nuxt></nuxt>
      </div>
      <content-footer v-if="!$route.meta.hideFooter"></content-footer>
    </div>
  </div>
</template>
<script>
/* eslint-disable no-new */
import PerfectScrollbar from "perfect-scrollbar";
import "perfect-scrollbar/css/perfect-scrollbar.css";

function hasElement(className) {
  return document.getElementsByClassName(className).length > 0;
}

function initScrollbar(className) {
  if (hasElement(className)) {
    new PerfectScrollbar(`.${className}`);
  } else {
    // try to init it later in case this component is loaded async
    setTimeout(() => {
      initScrollbar(className);
    }, 100);
  }
}

import DashboardNavbar from "~/components/layouts/argon/DashboardNavbar.vue";
import ContentFooter from "~/components/layouts/argon/ContentFooter.vue";
import DashboardContent from "~/components/layouts/argon/Content.vue";

export default {
  components: {
    DashboardNavbar,
    ContentFooter,
    DashboardContent,
  },
  methods: {
    initScrollbar() {
      let isWindows = navigator.platform.startsWith("Win");
      if (isWindows) {
        initScrollbar("scrollbar-inner");
      }
    }
  },
  mounted() {
    if (this.$auth.user.tenant_use_ged){
      this.$store.dispatch("tenant/fetchTenantGedData", this.$auth.user.tenant);
    }
    this.initScrollbar();
  },
  computed:
    {
      gedUrl() {
        return this.$store.state.tenant.tenantGedData;
      },
    },
};
</script>
<style lang="scss">
</style>
