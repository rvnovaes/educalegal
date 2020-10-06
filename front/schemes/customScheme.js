import LocalScheme from "@nuxtjs/auth/lib/schemes/local";
import store from '~/store'

export default class CustomScheme extends LocalScheme {

  async fetchUser(endpoint) {
    // Token is required but not available
    if (this.options.tokenRequired && !this.$auth.getToken(this.name)) {
      return;
    }

    // User endpoint is disabled.
    if (!this.options.endpoints.user) {
      this.$auth.setUser({});
      return;
    }

    // Try to fetch user and then set
    const user = await this.$auth.requestWith(
      this.name,
      endpoint,
      this.options.endpoints.user
    );
    this.$auth.setUser(user);
  }

}
