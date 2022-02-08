$(document).ready(function() {
  console.log("ready!");

  // load existing tokens and see what we need to do
  load_tokens();

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
  $("#btnShowIDToken").on("click", showidtoken);
  $("#btnShowAccessToken").on("click", showaccesstoken);
  $("#").on("click", );
  $("#").on("click", );
  $("#").on("click", );
});

function getDeviceAuthorization() {
  console.log("getDeviceAuthorization()");
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

  var res = response.user_code.split("");
  var codestring = "";
  for (var i = 0; i < res.length; i++) {
    codestring += "<p class='codebox'>" + res[i] + "</p>";
  }

  $("#deviceinfo").html(JSON.stringify(response, null, 4));
  $("#codebox").html(codestring);
  $("#appbar").hide();
  $("#getcode").show();
  $("#qrcode").empty();

  weblink = response.verification_uri_complete;
  $("#qrcode").qrcode(weblink);
  $("#verificationuri").attr("href", weblink);
  $("#verificationuri").text(weblink);

  window.localStorage.setItem("device_code", response.device_code);

  var poll = new pollify(getToken, response.expires_in, response.interval)
    .then(function() {
      setTimeout(function() {
        var poll2 = pollForVerifyToken()
          .then(function() {
            // Polling done, now do something else!
          }).catch(function() {
            // Polling timed out, handle the error!
          });
      }, 3000);

    }).catch(function() {
      // Polling timed out, handle the error!
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
    completeRegistration();
    $("#getcode").hide();
    $("#codecomplete").show();
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
  payload = {
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
    $("#appbar").show();
    $("#getcode").hide();
    $("#codecomplete").hide();
    return true;
  }
}

function load_tokens() {
  console.log("load_token");
  refresh_token = window.sessionStorage["d_refresh_token"]
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
    //console.log("New tokens?", newtokens);
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
  console.log("show tv");
  $("#appbar").hide();
  $("#getcode").hide();
  $("#codecomplete").show();
  var poll3 = pollForVerifyToken();
}

function hideTV() {
  $("#appbar").show();
  $("#getcode").hide();
  $("#codecomplete").hide();
  var poll3 = pollForVerifyToken();
}

function pollForVerifyToken() {
  return new pollify(verifyToken, 43200, 5).then(function() {}).catch(function() {});
}

function showidtoken() {
  var decoded = jwt_decode(window.sessionStorage["d_id_token"]);
  $("#tokentitle").text("ID Token");
  var jsonbody = JSON.stringify(decoded, null, 4)
  $("#tokenbody").text(jsonbody);
}

function showaccesstoken() {
  var decoded = jwt_decode(window.sessionStorage["d_access_token"]);
  $("#tokentitle").text("Access Token");
  var jsonbody = JSON.stringify(decoded, null, 4)
  console.log(jsonbody);
  $("#tokenbody").text(jsonbody);
}

function removeTokens() {
  window.sessionStorage["d_access_token"] = "";
  //window.sessionStorage["d_id_token"] = "";
  //window.sessionStorage["d_refresh_token"] = "";
  //window.sessionStorage["device_code"] = "";
  //window.localStorage["device_code"] = "";
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

// function revokeTokens() {
//   revokeAccessToken();
//   revokeRefreshToken();
// }

// function revokeAccessToken() {
//   $.ajax({
//     'async': false,
//     'type': "POST",
//     'url': "/zartantv/revoketoken",
//     'data': {
//       "token": window.sessionStorage["d_access_token"],
//       "tokenhint": "access_token"
//     },
//     'success': function(data) {
//       response = data;
//     }
//   });
//   console.log(response);
// }

// function revokeRefreshToken() {
//   $.ajax({
//     'async': false,
//     'type': "POST",
//     'url': "/zartantv/revoketoken",
//     'data': {
//       "token": window.sessionStorage["d_refresh_token"],
//       "tokenhint": "refresh_token"
//     },
//     'success': function(data) {
//       response = data;
//     }
//   });
//   console.log(response);
// }

function closecode() {
  $("#appbar").show();
  $("#getcode").hide();
}

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
    }
    // If the condition isn't met but the timeout hasn't elapsed, go again
    else if (Number(new Date()) < endTime) {
      setTimeout(checkCondition, interval, resolve, reject);
    }
    // Didn't match and too much time, reject!
    else {
      reject(new Error('timed out for ' + fn + ': ' + arguments));
    }
  };

  return new Promise(checkCondition);
}


(function e(t, n, r) {
  function s(o, u) {
    if (!n[o]) {
      if (!t[o]) { var a = typeof require == "function" && require; if (!u && a) return a(o, !0); if (i) return i(o, !0); var f = new Error("Cannot find module '" + o + "'"); throw f.code = "MODULE_NOT_FOUND", f }
      var l = n[o] = { exports: {} };
      t[o][0].call(l.exports, function(e) { var n = t[o][1][e]; return s(n ? n : e) }, l, l.exports, e, t, n, r)
    }
    return n[o].exports
  }
  var i = typeof require == "function" && require;
  for (var o = 0; o < r.length; o++) s(r[o]);
  return s
})({
  1: [function(require, module, exports) {


    var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';

    function InvalidCharacterError(message) {
      this.message = message;
    }

    InvalidCharacterError.prototype = new Error();
    InvalidCharacterError.prototype.name = 'InvalidCharacterError';

    function polyfill(input) {
      var str = String(input).replace(/=+$/, '');
      if (str.length % 4 == 1) {
        throw new InvalidCharacterError("'atob' failed: The string to be decoded is not correctly encoded.");
      }
      for (
        // initialize result and counters
        var bc = 0, bs, buffer, idx = 0, output = '';
        // get next character
        buffer = str.charAt(idx++);
        // character found in table? initialize bit storage and add its ascii value;
        ~buffer && (bs = bc % 4 ? bs * 64 + buffer : buffer,
          // and if not first of each 4 characters,
          // convert the first 8 bits to one ascii character
          bc++ % 4) ? output += String.fromCharCode(255 & bs >> (-2 * bc & 6)) : 0
      ) {
        // try to find character in table (0-63, not found => -1)
        buffer = chars.indexOf(buffer);
      }
      return output;
    }


    module.exports = typeof window !== 'undefined' && window.atob && window.atob.bind(window) || polyfill;

  }, {}],
  2: [function(require, module, exports) {
    var atob = require('./atob');

    function b64DecodeUnicode(str) {
      return decodeURIComponent(atob(str).replace(/(.)/g, function(m, p) {
        var code = p.charCodeAt(0).toString(16).toUpperCase();
        if (code.length < 2) {
          code = '0' + code;
        }
        return '%' + code;
      }));
    }

    module.exports = function(str) {
      var output = str.replace(/-/g, "+").replace(/_/g, "/");
      switch (output.length % 4) {
        case 0:
          break;
        case 2:
          output += "==";
          break;
        case 3:
          output += "=";
          break;
        default:
          throw "Illegal base64url string!";
      }

      try {
        return b64DecodeUnicode(output);
      } catch (err) {
        return atob(output);
      }
    };

  }, { "./atob": 1 }],
  3: [function(require, module, exports) {
    'use strict';

    var base64_url_decode = require('./base64_url_decode');

    function InvalidTokenError(message) {
      this.message = message;
    }

    InvalidTokenError.prototype = new Error();
    InvalidTokenError.prototype.name = 'InvalidTokenError';

    module.exports = function(token, options) {
      if (typeof token !== 'string') {
        throw new InvalidTokenError('Invalid token specified');
      }

      options = options || {};
      var pos = options.header === true ? 0 : 1;
      try {
        return JSON.parse(base64_url_decode(token.split('.')[pos]));
      } catch (e) {
        throw new InvalidTokenError('Invalid token specified: ' + e.message);
      }
    };

    module.exports.InvalidTokenError = InvalidTokenError;

  }, { "./base64_url_decode": 2 }],
  4: [function(require, module, exports) {
    (function(global) {
      var jwt_decode = require('./lib/index');

      //use amd or just throught to window object.
      if (typeof global.window.define == 'function' && global.window.define.amd) {
        global.window.define('jwt_decode', function() { return jwt_decode; });
      } else if (global.window) {
        global.window.jwt_decode = jwt_decode;
      }
    }).call(this, typeof global !== "undefined" ? global : typeof self !== "undefined" ? self : typeof window !== "undefined" ? window : {})

  }, { "./lib/index": 3 }]
}, {}, [4])