function checkAuth(ses) {
  if (ses && !window.localStorage.getItem('sestee')) {
    ping();
  }
  if (!ses && window.localStorage.getItem('sestee')) {
    window.localStorage.removeItem('sestee');
  }
}
