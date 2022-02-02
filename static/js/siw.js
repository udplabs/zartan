// SIW language picker
function changelanguage(lang) {
    $("#language").val(lang);
    console.log(signInWidget);
    signInWidget.remove();
    signInWidget.renderEl({el: '#sign-in-widget'});
}

// SIW altername username lookup
function lookupAltUsername(username, operation) {
    if (isNaN(username)) {
      return username;
    } else {
      nname = "";
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
  authClient.tokenManager.getTokens().then(({ accessToken, idToken }) => {
    // handle tokens
    authClient.token.verify(idToken).then(function() {
      // ID token is valid
      // do nothing for now
      console.log("tokens are good...");
    }).catch(function(err) {
      // ID token is invalid/missing
      authClient.session.get().then(function(session) {
        // session exists
        if (session.status == "ACTIVE") {
          console.log("Session Active");
          $("#sessionId").val(session.id);
          authClient.token.getWithoutPrompt({
              responseType: ['token', 'id_token']
          }).then(function(res) {
              console.log("results", res);
              var tokens = res.tokens;
              console.log(tokens);
              // Do something with tokens, such as
              authClient.tokenManager.setTokens(tokens);
              location.reload();
          })
          .catch(function(err) {
              console.log(err);
          });
        }
      })
    })
  })
  .catch(function(err) {
    // handle expired/invalid/empty tokens
    console.log(err);
  })
}