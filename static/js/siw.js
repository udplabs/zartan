var authClient = new OktaAuth(authClientConfig);

$(document).ready(checkForSSO);

// SIW language picker
function changelanguage(lang) {
  $("#language").val(lang);
  console.log(signInWidget);
  signInWidget.remove();
  signInWidget.renderEl({ el: '#sign-in-widget' });
}

// SIW altername username lookup
function lookupAltUsername(username, operation) {
  if (isNaN(username)) {
    return username;
  } else {
    var nname = "";
    $.ajax({
      'async': false,
      'type': "GET",
      'url': "/get_username/" + username,
      'success': function (data) {
        nname = data;
      }
    });
    console.log(nname);
    return nname;
  }
}

function checkForSSO() {
  console.log("Checking for active session for SSO...");
  authClient.tokenManager.get("idToken")
    .then(function(token) {
      // handle tokens
      authClient.token.verify(token)
        .then(function () {
          // ID token is valid
          // do nothing for now
          console.log("tokens are good...");
        }).catch(function (err) {
          // ID token is invalid/missing
          authClient.session.get()
            .then(function (session) {
              // session exists
              if (session.status == "ACTIVE") {
                console.log("Session Active");
                $("#sessionId").val(session.id);
                authClient.token.getWithoutPrompt({
                  responseType: ['token', 'id_token']
                }).then(function (res) {
                  console.log("results", res);
                  var tokens = res.tokens;
                  console.log(tokens);
                  // Do something with tokens, such as
                  authClient.tokenManager.setTokens(tokens);
                  // HACK FIXME
                  // redirect to the /login page so the SIW can get everything
                  // set up. There's got to be a better way to do this...
                  location.href = '/login';
                })
                  .catch(function (err) {
                    console.log(err);
                  });
              }
            })
        })
    })
    .catch(function (err) {
      // handle expired/invalid/empty tokens
      console.log("ID token missing...");
      console.log(err);
    })
}