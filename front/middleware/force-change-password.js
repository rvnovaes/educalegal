export default async function forceChangePassword({redirect, store}){
  if (store.$auth.$state.loggedIn){
    if (store.state.auth.user.force_password_change){
      return redirect('/trocar_senha');
      }
    }
}
