function onSignIn(googleUser) {
  var id_token = googleUser.getAuthResponse().id_token;
  var xhr = new XMLHttpRequest();
  xhr.open('POST', 'https://localhost:5000/googletoken_login');
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
  xhr.onload = function() {
    window.location.href = '/user/' + xhr.responseText;
  }
  xhr.send('id_token=' + id_token);
}
