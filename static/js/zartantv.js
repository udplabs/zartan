$(document).ready(function() {
  console.log("ready!");

  // load existing tokens and see what we need to do
  loadTokens();

  // register click handlers
  $('.id-open').on('click', function() {
    $('.toggle-deviceid, .formwrap2, .toggle-bg2').addClass('active');
    $('.icon2-close').addClass('open');
  });

  $('.icon2-close').on('click', function() {
    $('.toggle-deviceid, .formwrap2, .toggle-bg2').removeClass('active');
    $('.icon2-close').removeClass('open');
  });

  $('.cta-open').on('click', function() {
    $('.toggle-form, .formwrap, .toggle-bg').addClass('active');
    $('.icon-close').addClass('open');
  });

  $('.icon-close').on('click', function() {
    $('.toggle-form, .formwrap, .toggle-bg').removeClass('active');
    $('.icon-close').removeClass('open');
  });

  $("#btnRebootTV").on("click", function() {
    window.location.reload();
  });

  $("#btnTVPower").on("click", getDeviceAuthorization);
  $("#btnRemoveTokens").on("click", removeTokens);
  $("#btnRevokeAccess").on("click", revokeDeviceAccess);

  $("#btnShowIDToken").on("click", {
    token_type_hint: "d_id_token",
    token_name: "ID Token"
  }, showDecodedJwt);

  $("#btnShowAccessToken").on("click", {
    token_type_hint: "d_access_token",
    token_name: "Access Token"
  }, showDecodedJwt);

  $("#btnGetCode").on("click", getcode);
  $("#btnCancelGetCode").on("click", closeCodeWindow);
});

function getDeviceAuthorization() {
  console.log("getDeviceAuthorization()");
  var response = {};
  $.ajax({
    async: false,
    type: "GET",
    url: "/zartantv/deviceauthorization",
    data: {},
    success: function(data) {
      response = data;
    }
  });
  console.log(response);

  var code_characters = response.user_code.split("");
  var codestring = "";
  for (var character of code_characters) {
    codestring += "<p class=\"codebox\">" + character + "</p>";
  }

  $("#deviceinfo").html(JSON.stringify(response, null, 4));
  $("#codebox").html(codestring);
  $("#appbar").hide();
  $("#getcode").modal("show");
  $("#qrcode").empty();

  var weblink = response.verification_uri_complete;
  $("#qrcode").qrcode(weblink);
  $("#verificationuri").attr("href", weblink);
  $("#verificationuri").text(weblink);

  window.localStorage.setItem("device_code", response.device_code);

  // start polling for device authorization
  new pollify(getToken, response.expires_in, response.interval)
    .then(function() {
      // polling finished, finish the device registration
      completeRegistration();
      showTV();
    })
    .catch(function() {
      // polling timed out. do something?
    });
}

function getToken() {
  var device_code = window.localStorage.getItem("device_code");
  console.log("getToken()", device_code);
  $.ajax({
    async: false,
    type: "GET",
    url: "/zartantv/token",
    data: {
      "device_code": device_code
    },
    success: function(data) {
      response = data;
    }
  });
  console.log(response);

  if (response.token_type == "Bearer") {
    window.sessionStorage["d_access_token"] = response.access_token;
    window.sessionStorage["d_id_token"] = response.id_token;
    window.sessionStorage["d_refresh_token"] = response.refresh_token;
    window.sessionStorage["device_code"] = device_code;
    $("#deviceinfo2").html(JSON.stringify(response, null, 4));
    return true;
  } else {
    $("#deviceinfo2").html("Authorization Pending")
    return false;
  }
}

function completeRegistration() {
  console.log("completeRegistration()");
  var id_token = window.sessionStorage.getItem("d_id_token");
  var device_code = window.localStorage.getItem("device_code");
  var response = {};
  var payload = {
    "id_token": id_token,
    "device_code": device_code
  };
  console.log("Payload", payload);
  $.ajax({
    async: false,
    type: "POST",
    url: "/zartantv/complete_registration",
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify(payload),
    success: function(data) {
      response = data;
    }
  });
  console.log("Response", response);
}

function verifyToken() {
  console.log("verifyToken()");
  var newtokens = "";
  payload = {
    "access_token": window.sessionStorage["d_access_token"],
    "id_token": window.sessionStorage["d_id_token"],
    "refresh_token": window.sessionStorage["d_refresh_token"],
    "device_code": window.sessionStorage["device_code"],
  }
  console.log("Payload", payload);
  $.ajax({
    async: false,
    type: "POST",
    url: "/zartantv/verify_token",
    contentType: "application/json; charset=utf-8",
    data: JSON.stringify(payload),
    success: function(data) {
      newtokens = data;
    }
  });
  if (newtokens == "true") {
    console.log("Device Found");
    return false;
  } else if (newtokens["access_token"]) {
    console.log("Device is Valid");
    window.sessionStorage["d_access_token"] = newtokens.access_token;
    window.sessionStorage["d_id_token"] = newtokens.id_token;
    window.sessionStorage["d_refresh_token"] = newtokens.refresh_token;
    return false;
  } else {
    console.log("Device Not Found or Session Expired");
    hideTV();
    return true;
  }
}

function loadTokens() {
  console.log("loadTokens()");
  var refresh_token = window.sessionStorage["d_refresh_token"]
  var newtokens = "";
  if (refresh_token != "") {
    console.log("Check Current Tokens");
    payload = {
      "access_token": window.sessionStorage["d_access_token"],
      "id_token": window.sessionStorage["d_id_token"],
      "refresh_token": window.sessionStorage["d_refresh_token"],
      "device_code": window.sessionStorage["device_code"],
    }
    $.ajax({
      async: false,
      type: "POST",
      url: "/zartantv/verify_token",
      contentType: "application/json; charset=utf-8",
      data: JSON.stringify(payload),
      success: function(data) {
        newtokens = data;
      }
    });

    if (newtokens == "true") {
      console.log("Device Found");
      showTV();
    } else if (newtokens["access_token"]) {
      console.log("Device is Valid");
      window.sessionStorage["d_access_token"] = newtokens.access_token;
      window.sessionStorage["d_id_token"] = newtokens.id_token;
      window.sessionStorage["d_refresh_token"] = newtokens.refresh_token;
      showTV();
    } else {
      console.log("Device Not Found");
      hideTV();
    }
  } else {
    console.log("No refresh token present.");
  }
}

function showTV() {
  console.log("showTV()");
  $("#appbar").hide();
  $("#getcode").modal("hide");
  $("#tv").show();
  pollForVerifyToken();
}

function hideTV() {
  $("#appbar").show();
  $("#getcode").modal("hide");
  $("#tv").hide();
}

function pollForVerifyToken() {
  return new pollify(verifyToken, 43200, 10)
    .then(function() {
      // this is intentionally empty
    })
    .catch(function() {
      // this is intentionally empty
    });
}

function showDecodedJwt(event) {
  var token_type = event.data.token_type_hint
  var token_name = event.data.token_name;
  var token = window.sessionStorage[token_type];
  console.log("Token type", token_type);
  console.log("Token name", token_name);

  $("#tokentitle").text(token_name);
  try {
    var decoded = parseJwt(token);
    var jsonbody = JSON.stringify(decoded, null, 4)
    $("#tokenbody").text(jsonbody);
  } catch {
    $("#tokenbody").text("Problem decoding token");
  }
}

function removeTokens() {
  // just remove the access token. this shows
  // how the refresh token is used to get a new
  // access token
  window.sessionStorage["d_access_token"] = "";
}

function revokeDeviceAccess() {
  $.ajax({
    async: false,
    type: "POST",
    url: "/zartantv/revoketoken",
    data: {
      "token": window.sessionStorage["d_refresh_token"]
    },
    success: function(data) {
      response = data;
      removeTokens();
    }
  });
  console.log(response);
}

function closeCodeWindow() {
  $("#appbar").show();
  $("#getcode").modal("hide");
  // cancel the polling for authorization when the cancel button is clicked
  cancelPolling();
}

var myTimeout = "";
// The polling function
function pollify(fn, timeout, interval) {
  timeout = timeout * 1000;
  interval = interval * 1000;
  var endTime = Number(new Date()) + (timeout || 2000);
  interval = interval || 100;

  var checkCondition = function(resolve, reject) {
    // If the condition is met, we're done!
    var result = fn();
    if (result) {
      resolve(result);
    } else if (Number(new Date()) < endTime) {
      // If the condition isn't met but the timeout hasn't elapsed, go again
      myTimeout = setTimeout(checkCondition, interval, resolve, reject);
    } else {
      // Didn't match and too much time, reject!
      reject(new Error('timed out for ' + fn + ': ' + arguments));
    }
  };

  return new Promise(checkCondition);
}

function cancelPolling() {
  clearTimeout(myTimeout);
}

function parseJwt(token) {
  try {
    return JSON.parse(atob(token.split(".")[1]));
  } catch (e) {
    return null;
  }
}
