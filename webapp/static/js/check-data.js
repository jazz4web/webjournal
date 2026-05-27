function checkData(data) {
  if (window.localStorage.getItem('sestee')) {
    if (!data.cu || data.cu.brkey != checkBR()) {
      window.localStorage.removeItem('sestee');
      window.location.reload();
    }
  }
}
