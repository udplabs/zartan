/*
 * Version: 2.1.2
 */

$(document).ready(function() {
	console.log("Document Ready!");

	$("#loginButton").on("click", loginClickHandler);
	$("#acceptConsent").on("click", acceptConsentClickHandler);
	$("#rejectConsent").on("click", rejectConsentClickHandler);
	$("#signUpButton").on("click", signUpButtonClickHandler);
	$("#customSignUpButton").on("click", signUpButtonClickHandler);
	$("#registerUser").on("click", registerUserClickHandler);
	$("#submitRegistrationDefault").on("click", submitRegistrationDefaultClickHandler);
	$("#submitRegistrationAlt1").on("click", submitRegistrationAlt1ClickHandler);
	$("#verifyAccount").on("click", verifyAccountClickHandler);
	$("#setPreRegCredentials").on("click", setPreRegCredentialsClickHandler);

	// MFA verification event handlers
	$("#factorList").change(factorListOnChange);
	$("#sendOTPButton").click(sendOTPClickHandler);
	$("#sendPushButton").click(sendPushClickHandler);
	$("#oktaOTPCodeLink").click(enterOktaOTPClickHandler);
	$("#mfaVerifyButton").click(verifyOTPClickHandler);
	$("#mfaVerifyAnswerButton").click(verifyAnswerClickHandler);
	hideAllVerifyForms();

	// MFA enrollment event handlers
	$("#factorEnrollList").change(factorEnrollListOnChange);
	$("#sendEnrollOTPButton").click(sendEnrollOTPClickHandler);
	$("#mfaEnrollVerifyButton").click(verifyEnrollOTPClickHandler);
	$("#mfaEnrollQuestionButton").click(enrollQuestionClickHandler);
	$("#mfaFinishEnrollButton").click(finishEnrollClickHandler);
	$("#mfaFinishEnrollButton").hide();
	hideAllEnrollForms();

	$("#password").keypress(function (e) {
		var key = e.which;
		if(key == 13) {  // the enter key code
			$("#loginButton").click();
			return false;
		}
	});

	$("#registrationConfirmPassword").keypress(function (e) {
		var key = e.which;
		if(key == 13) {  // the enter key code
			$("#registerUser").click();
			return false;
		}
	});

	//Display Modals
	console.log("stateToken: " + $("#stateToken").val());
	console.log("showMFAEnroll: " + $("#showMFAEnroll").val());
	console.log("showBDV: " + $("#showBDV").val());

	if($("#showConsent").val() == "True") {
		$("#consentModal").modal("show");
	}else if($("#showRegistrationDefault").val() == "True") {
	    $("#registrationDefaultModal").modal("show");
	} else if($("#showRegistrationAlt1").val() == "True") {
	    $("#registrationAlt1Modal").modal("show");
	} else if($("#stateToken").val() != "" && $("#showBDV").val() == "true") {
	    $("#verifyAccountModal").modal("show");
	} else if($("#stateToken").val() != "" && $("#showMFAEnroll").val() == "true") {
	    $.ajax({
            url: "get_available_factors_by_state/" + $("#stateToken").val(),
            type: "POST",
            contentType: "application/json; charset=utf-8",
            success: data => {
                console.log(data);
                var authResponseJson = JSON.parse(data);
                var txStatus = authResponseJson.status;

                if (txStatus == "MFA_ENROLL") {
                    $("#mfaUserId").val(authResponseJson._embedded.user.id);
                    var factors = authResponseJson._embedded.factors;
                    setupFactorEnrollmentList(factors);
                    $("#mfaEnrollmentModal").modal("show");
                } else {
                	//TODO: use modal popup
                	$("body").removeClass("page-loader-2");
                	alert(authResponseJson.errorMessage);
                }
            }
        });
	}

}); // End document ready

function signUpButtonClickHandler() {
    console.log("signUpButtonClickHandler()");

    $("#basicRegistrationModal").modal("show");

}

function loginClickHandler() {
	console.log("loginClickHandler()");

	var url = "/login";

	if($("#sessionId").val()) {
	    url = "/login/" + $("#sessionId").val();
	}

	oktaSignIn.session.get(function (res) {
      // Session exists, show logged in state.
      if (res.status === 'ACTIVE') {
        // showApp()
        console.log("Session Active");
        oktaSignIn.session.close(function (err) {
          if (err) {
            // The user has not been logged out, perform some error handling here.
            console.log("Failed to close the session (if it exsists) otherwise fine");
            console.log(err);
          }
          // The user is now logged out.
            callLogin(url);
        });
      } else if (res.status === 'INACTIVE') {
        console.log("Session Not Active");
        callLogin(url);
      }
	});
}

function callLogin(url) {
    var payload = {
        "username": $("#username").val(),
        "password": $("#password").val()
    };
    
    $.ajax({
        url: url,
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var authResponseJson = JSON.parse(data);
            console.log(authResponseJson);
            var txStatus = authResponseJson.status;

            if (txStatus == "SUCCESS") {
				location.href = authResponseJson.redirectUrl;
            } else if (txStatus == "MFA_REQUIRED") {
                // Add enrolled MFA Options
                $("#stateToken").val(authResponseJson.stateToken);
                var factors = authResponseJson._embedded.factors;
                setupFactorList(factors);
                $("#mfaVerifyModal").modal("show");
            } else if (txStatus == "MFA_ENROLL") {
                // show MFA enrollment modal
                $("#mfaUserId").val(authResponseJson._embedded.user.id);
                $("#stateToken").val(authResponseJson.stateToken);
                var factors = authResponseJson._embedded.factors;
                setupFactorEnrollmentList(factors);
                $("#mfaEnrollmentModal").modal("show");
            } else {
            	//TODO: use modal popup
            	$("body").removeClass("page-loader-2");
            	alert(authResponseJson.errorMessage);
            }
        }
    });
}


/**
 * MFA enrollment functions
 */
function setupFactorEnrollmentList(factors) {
    $("#factorEnrollList").empty().append("<option>Select Factor</option>");

    // make a list of factors to choose from, and also map
    // to friendly display names
    var factors_array = [];
    for (var factorIdx in factors) {
        var factor = factors[factorIdx];
        var factorType = factor.factorType;
        var provider = factor.provider;
        var vendorName = factor.vendorName;
        var factorStatus = factor.status;
        var enrollment = factor.enrollment;
        // default to factorType as the name as a fallback
        var factorName = factorType;
        var sortOrder = 100;

        if (factorType == "token:software:totp") {
            if (vendorName == "GOOGLE") {
                factor.factorName = "Google Authenticator";
                factor.sortOrder = 20;
            } else if (vendorName == "OKTA") {
                // don't list Okta Verify OTP
                continue;
            }
        } else if (factorType == "push") {
            factor.factorName = "Okta Verify";
            factor.sortOrder = 10;
        } else if (factorType == "sms") {
            factor.factorName = "SMS";
            factor.sortOrder = 30;
        } else if (factorType == "call") {
            factor.factorName = "Voice Call";
            factor.sortOrder = 40;
        } else if (factorType == "question") {
            factor.factorName = "Security Question";
            factor.sortOrder = 50;
        }

        factors_array.push(factor);
    }

    // now add the sorted array to the select list
    factors_array.sort(function(a, b) {
        return a.sortOrder - b.sortOrder;
    });

    for (var i = 0; i < factors_array.length; i++) {
        var factor = factors_array[i];
        var option = '<option value="' + factor.factorName + '" data-type="' + factor.factorType + '"';
        option += ' data-vendor="' + factor.vendorName + '" data-provider="' + factor.provider + '"';
        option += '>' + factor.factorName + '</option>';
        $("#factorEnrollList").append(option);
    }
}

function hideAllEnrollForms() {
    $("#mfaEnrollPushForm").hide();
    $("#mfaEnrollOTPForm").hide();
    $("#mfaEnrollVerifyCodeForm").hide();
    $("#mfaEnrollQuestionForm").hide();
    $("#mfaEnrollQRCodeForm").hide();
}

function factorEnrollListOnChange() {
    hideAllEnrollForms();
    logEnrollMessage("");
    var factorName = $("#factorEnrollList option:selected").text();
    var factorType = $("#factorEnrollList option:selected").data("type");
    var provider = $("#factorEnrollList option:selected").data("provider");

    $("#mfaFactorName").val(factorName);
    $("#mfaFactorType").val(factorType);
    $("#mfaProvider").val(provider);

    switch (factorName) {
        case "Okta Verify":
        case "Okta Verify Push":
            //$("#mfaEnrollPushForm").show();
            enrollPushFactor();
            break;
        //case "Okta Verify OTP":
        case "Google Authenticator":
            $("#mfaEnrollVerifyCodeForm").show();
            enrollTOTPFactor();
            $("#mfaEnrollPassCode").focus();
            break;
        case "SMS":
            $("#mfaEnrollOTPForm").show();
            $("#sendEnrollOTPButton").text("Send SMS");
            $("#mfaEnrollRecipient").focus();
            break;
        case "Voice Call":
            $("#mfaEnrollOTPForm").show();
            $("#sendEnrollOTPButton").text("Call Me");
            $("#mfaEnrollRecipient").focus();
            break;
        case "Security Question":
            getAvailableQuestions();
            $("#mfaEnrollQuestionForm").show();
            $("#mfaEnrollAnswer").focus();
            break;
    }
}


function logEnrollMessage(message) {
    $("#mfaEnrollStatusMessage").text(message);
}

function enrollPushFactor() {
    var stateToken = $("#stateToken").val();
    var factorType = $("#mfaFactorType").val();
    var provider = $("#mfaProvider").val();
    var payload = {
        "state_token": stateToken,
        "factor_type": factorType,
        "provider": provider
    };

    $.ajax({
        url: "/enroll_push",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            var factorId = authResponseJson._embedded.factor.id;
            var qrCode = authResponseJson._embedded.factor._embedded.activation._links.qrcode.href;
            $("#mfaFactorID").val(factorId);
            $("#mfaEnrollQRCode").attr("src", qrCode);
            $("#mfaEnrollQRCodeForm").show();

            // start polling for a response
            setTimeout(pollForPushEnrollment, 3000);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function pollForPushEnrollment() {
    var factor_id = $("#mfaFactorID").val();
    var state_token = $("#stateToken").val();
    var factor_name = $("#mfaFactorName").val();

    $.ajax({
        url: "/poll_for_push_enrollment",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"state_token": state_token, "factor_id": factor_id}),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            var txStatus = authResponseJson.status;
            var factorResut = authResponseJson.factorResult;
            if (txStatus == "SUCCESS") {
                logEnrollMessage(factor_name + " successfully enrolled!");
                $(".overlay-effect").removeClass("hidden").addClass("visible");
                // get the sessionToken
                var sessionToken = authResponseJson.sessionToken;
                // go get OIDC tokens to complete the login
                saveSessionToken(sessionToken);
            } else if (factorResut == "WAITING") {
                logEnrollMessage("Waiting for enrollment");
                setTimeout(pollForPushEnrollment, 3000);
            } else if (factorResut == "TIMEOUT") {
                logEnrollMessage("Your push notification has timed out");
                //$("#sendPushButton").text("Resend Push");
                //$("#sendPushButton").on("click", resendPushClickHandler);
            }
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function enrollTOTPFactor() {
    var stateToken = $("#stateToken").val();
    var factorType = $("#mfaFactorType").val();
    var provider = $("#mfaProvider").val();
    var payload = {
        "state_token": stateToken,
        "factor_type": factorType,
        "provider": provider
    };
    //logEnrollMessage("Enrolling");

    $.ajax({
        url: "/enroll_totp",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            var factorId = authResponseJson._embedded.factor.id;
            var qrCode = authResponseJson._embedded.factor._embedded.activation._links.qrcode.href;
            $("#mfaFactorID").val(factorId);
            $("#mfaEnrollQRCode").attr("src", qrCode);
            $("#mfaEnrollQRCodeForm").show();
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

// for SMS and voice
function sendEnrollOTPClickHandler() {
    var stateToken = $("#stateToken").val();
    var factorType = $("#mfaFactorType").val();
    var provider = $("#mfaProvider").val();
    var phoneNumber = $("#mfaEnrollRecipient").val();
    var payload = {
        "state_token": stateToken,
        "factor_type": factorType,
        "provider": provider,
        "phone_number": phoneNumber
    };

    $("#mfaEnrollVerifyCodeForm").show();
    $("#mfaEnrollPassCode").focus();
    logEnrollMessage("A code has been sent to your device");

    $.ajax({
        url: "/enroll_sms_voice",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            var factorId = authResponseJson._embedded.factor.id;
            $("#mfaFactorID").val(factorId);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function verifyEnrollOTPClickHandler() {
    var factor_name = $("#mfaFactorName").val();
    var factorId = $("#mfaFactorID").val();
    var stateToken = $("#stateToken").val();
    var pass_code = $("#mfaEnrollPassCode").val();
    var payload = {
        "factor_id": factorId,
        "state_token": stateToken,
        "pass_code": pass_code
    };
    console.log(payload);

    $.ajax({
        url: "/activate_totp",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            if (authResponseJson.errorCode) {
                logEnrollMessage(authResponseJson.errorSummary);
            } else if (authResponseJson.status == "SUCCESS") {
                logEnrollMessage(factor_name + " successfully enrolled!");
                // get the sessionToken
                var sessionToken = authResponseJson.sessionToken;
                // go get OIDC tokens to complete the login
                saveSessionToken(sessionToken);
            }
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function getAvailableQuestions() {
    var user_id = $("#mfaUserId").val();
    var payload = {
        "user_id": user_id
    };

    $.ajax({
        url: "/list_available_questions",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            setupQuestionList(response);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function setupQuestionList(questions) {
    $("#mfaEnrollQuestion").empty();
    for (var qIdx in questions) {
        var q = questions[qIdx];
        var value = q.question;
        var label = q.questionText;
        var option = new Option(label, value);
        //console.log("Adding question " + label + " wth value " + value);
        $("#mfaEnrollQuestion").append(option);
    }
    // and add the custom question option to the end of the list
    //$("#mfaEnrollQuestion").append(new Option("Create your own security question", "custom"));
}

function enrollQuestionClickHandler() {
    var factor_name = $("#mfaFactorName").val();
    var stateToken = $("#stateToken").val();
    var factorType = $("#mfaFactorType").val();
    var provider = $("#mfaProvider").val();
    var question = $("#mfaEnrollQuestion").val();
    var answer = $("#mfaEnrollAnswer").val();
    var payload = {
        "state_token": stateToken,
        "factor_type": factorType,
        "provider": provider,
        "question": question,
        "answer": answer
    };

    $.ajax({
        url: "/enroll_question",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            if (authResponseJson.status == "SUCCESS") {
                logEnrollMessage(factor_name + " successfully enrolled!");
                saveSessionToken(authResponseJson.sessionToken);
            }
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function saveSessionToken(token) {
    $("#mfaSessionToken").val(token);
    $("#factorEnrollList").prop("disabled", true);
    $("#mfaFinishEnrollButton").show();
    setTimeout(function() {
        logEnrollMessage("");
    }, 5000);
}

function finishEnrollClickHandler() {
    var sessionToken = $("#mfaSessionToken").val();
    processLogin(sessionToken);
}

/**
 * end MFA enrollment functions
 */

/**
 * MFA verification functions
 */
function setupFactorList(factors) {
    //$("#factorList").empty().append("<option>Select Factor</option>");

    // build a list of factors for the user to choose from, also map
    // the factors to friendly display names
    for (var factorIdx in factors) {
        var factor = factors[factorIdx];
        var factorId = factor.id;
        var factorType = factor.factorType;
        var vendorName = factor.vendorName;
        var phoneNumber = "";
        var email = "";
        var questionText = "";
        // default factor name to factor type as a fallback
        var factorName = factorType;

        if (factorType == "token:software:totp") {
            if (vendorName == "OKTA") {
                factorName = "Okta Verify OTP";
            } else if (vendorName == "GOOGLE") {
                factorName = "Google Authenticator";
            }
        } else if (factorType == "push") {
            factorName = "Okta Verify Push";
        } else if (factorType == "sms") {
            factorName = "SMS";
            try
            {
            phoneNumber = factor.profile.phoneNumber;
            } catch (error) { };
            try
            {
            phoneNumber = factor.phoneNumber;
            } catch (error) { };
        } else if (factorType == "call") {
            factorName = "Voice Call";
            if (typeof(factor.profile.phoneNumber) != "undefined")
            {
            phoneNumber = factor.profile.phoneNumber;
            }
            if (typeof(factor.phoneNumber) != "undefined")
            {
            phoneNumber = factor.phoneNumber;
            }
        } else if (factorType == "email") {
            factorName = "Email";
            email = factor.profile.email;
        } else if (factorType == "question") {
            factorName = "Security Question";
            questionText = factor.profile.questionText;
        }

        var option = '<option value="' + factorName + '" data-type="' + factorType + '"';
        option += ' data-question="' + questionText + '" data-phone="' + phoneNumber + '"';
        option += ' data-email="' + email + '" data-vendor="' + vendorName + '"';
        option += ' data-id="' + factorId + '"';
        option += '>' + factorName + '</option>';
        $("#factorList").append(option);
        //console.log("Added factor " + option);
    }
    $("#factorList").change();
}

function factorListOnChange() {
    hideAllVerifyForms();
    logMessage("");
    var factorId = $("#factorList option:selected").data("id");
    var factorName = $("#factorList option:selected").text();
    var email = $("#factorList option:selected").data("email");
    var phoneNumber = $("#factorList option:selected").data("phone");
    var questionText = $("#factorList option:selected").data("question");
    $("#mfaFactorID").val(factorId);

    switch (factorName) {
        case "Okta Verify Push":
            $("#mfaPushForm").show();
            $("#oktaOTPCodeLink").show();
            break;
        case "Okta Verify OTP":
        case "Google Authenticator":
            $("#mfaVerifyCodeForm").show();
            $("#mfaPassCode").focus();
            break;
        case "SMS":
            $("#mfaOTPForm").show();
            $("#mfaVerifyCodeForm").show();
            $("#sendOTPButton").text("Send SMS");
            $("#mfaRecipient").text(phoneNumber);
            break;
        case "Voice Call":
            $("#mfaOTPForm").show();
            $("#mfaVerifyCodeForm").show();
            $("#sendOTPButton").text("Call Me");
            $("#mfaRecipient").text(phoneNumber);
            break;
        case "Email":
            $("#mfaOTPForm").show();
            $("#mfaVerifyCodeForm").show();
            $("#sendOTPButton").text("Send Email");
            $("#mfaRecipient").text(email);
            break;
        case "Security Question":
            $("#mfaQuestionForm").show();
            $("#mfaQuestion").text(questionText);
            $("#mfaAnswer").focus();
            break;
    }
}

function hideAllVerifyForms() {
    $("#mfaPushForm").hide();
    $("#mfaOTPForm").hide();
    $("#mfaVerifyCodeForm").hide();
    $("#mfaQuestionForm").hide();
}

function logMessage(message) {
    $("#mfaStatusMessage").text(message);
}

function sendPushClickHandler() {
    var factor_id = $("#mfaFactorID").val();
    var state_token = $("#stateToken").val();
    logMessage("Push notification sent");

  
    $.ajax({
        url: "/send_push",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"state_token": state_token, "factor_id": factor_id}),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            // set up the polling
            setTimeout(pollForPushVerification, 3000);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function pollForPushVerification() {
    var factor_id = $("#mfaFactorID").val();
    var state_token = $("#stateToken").val();

    $.ajax({
        url: "/poll_for_push_verification",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"state_token": state_token, "factor_id": factor_id}),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            var txStatus = authResponseJson.status;
            var factorResut = authResponseJson.factorResult;
            if (txStatus == "SUCCESS") {
                // get the sessionToken
                var sessionToken = authResponseJson.sessionToken;
                // go get OIDC tokens to complete the login
                processLogin(sessionToken);
            } else if (factorResut == "WAITING") {
                logMessage("Waiting for push response");
                setTimeout(pollForPushVerification, 3000);
            } else if (factorResut == "TIMEOUT") {
                logMessage("Your push notification has timed out");
                $("#sendPushButton").text("Resend Push");
                $("#sendPushButton").on("click", resendPushClickHandler);
            } else if (factorResut == "REJECTED") {
                logMessage("You have chosen to reject this login");
                $("#sendPushButton").text("Resend Push");
                $("#sendPushButton").on("click", resendPushClickHandler);
            }
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function resendPushClickHandler() {
    var factor_id = $("#mfaFactorID").val();
    var state_token = $("#stateToken").val();
    logMessage("Push notification re-sent");

    $.ajax({
        url: "/resend_push",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"state_token": state_token, "factor_id": factor_id}),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            // set up the polling
            setTimeout(pollForPushVerification, 3000);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function enterOktaOTPClickHandler() {
    $("#oktaOTPCodeLink").hide();
    $("#factorList").val("Okta Verify OTP").change();
}

function sendOTPClickHandler() {
    var factor_id = $("#mfaFactorID").val();
    var state_token = $("#stateToken").val();
    $("#mfaPassCode").focus();
    logMessage("A code has been sent to your device");

    $.ajax({
        url: "/verify_totp",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"state_token": state_token, "factor_id": factor_id}),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function verifyOTPClickHandler() {
    var factor_id = $("#mfaFactorID").val();
    var state_token = $("#stateToken").val();
    var pass_code = $("#mfaPassCode").val();
    var payload = {
        "state_token": state_token,
        "factor_id": factor_id,
        "pass_code": pass_code
    };
    console.log(payload);
    $.ajax({
        url: "/verify_totp",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            if (authResponseJson.errorCode) {
                logMessage(authResponseJson.errorCauses[0].errorSummary);
            } else if (authResponseJson.status == "SUCCESS") {
                // get the sessionToken
                var sessionToken = authResponseJson.sessionToken;
                // go get OIDC tokens to complete the login
                processLogin(sessionToken);
            }
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function verifyAnswerClickHandler() {
    var factor_id = $("#mfaFactorID").val();
    var state_token = $("#stateToken").val();
    var answer = $("#mfaAnswer").val();
    var payload = {
        "state_token": state_token,
        "factor_id": factor_id,
        "answer": answer
    };

    $.ajax({
        url: "/verify_answer",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var authResponseJson = JSON.parse(data);
            if (authResponseJson.errorCode) {
                logMessage(authResponseJson.errorCauses[0].errorSummary);
            } else if (authResponseJson.status == "SUCCESS") {
                // get the sessionToken
                var sessionToken = authResponseJson.sessionToken;
                // go get OIDC tokens to complete the login
                processLogin(sessionToken);
            }
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function processLogin(sessionToken) {
    $.ajax({
        url: "/get_authorize_url",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({"session_token": sessionToken}),
        success: data => {
            console.log(data);
            var responseJson = JSON.parse(data);
            location.href = responseJson.authorize_url;
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

/**
 * end MFA verification functions
 */

/**
 * User profile functions
 */
$("#saveUserProfileButton").on("click", saveUserClickHandler);

function saveUserClickHandler() {
    var userId = $("#userId").val();
    var firstName = $("#first_name").val();
    var lastName = $("#last_name").val();
    var email = $("#email").val();
    var secondEmail = $("#second_email").val();
    //var primaryPhone = $("#primary_phone").val();
    var mobilePhone = $("#mobile_phone").val();
    var height = $("#height").val();
    var weight = $("#weight").val();
    var dob = $("#dob").val();

    var payload = {
        "user_profile": {
            "profile": {
                "firstName": firstName,
                "lastName": lastName,
                "email": email,
                "secondEmail": secondEmail,
                //"primaryPhone": primaryPhone,
                "mobilePhone": mobilePhone
            }
        },
        "app_profile": {
            "profile": {
                "height": height,
                "weight": weight,
                "dob": dob
            }
        }
    };

    $.ajax({
        url: "/profile/" + userId,
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            console.log(data);
            var responseJson = JSON.parse(data);
            console.log(responseJson);
            logStatusMessage("Profile saved!");
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function logStatusMessage(message) {
    $("#statusMessage").text(message);
    setTimeout(clearStatusMessage, 5000);
}
function clearStatusMessage() {
    $("#statusMessage").text("");
}

/**
 * End user profile functions
 */

function acceptConsentClickHandler() {
	console.log("acceptConsentClickHandler()");
	$(this).prop("disabled", true);
	$(this).html(
	    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Processing...'
	);
	$.ajax({
        url: "/accept-consent",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        success: data => {
            console.log(data);
            var acceptConsentResponseJson = JSON.parse(data);

            if(acceptConsentResponseJson.success) {
            	$("#consentModal").modal("hide");
            	if($("#showRegistrationDefault").val() == "True") {
            	    $("#registrationDefaultModal").modal("show");
            	} else if($("#showRegistrationAlt1").val() == "True") {
            	    $("#registrationAlt1Modal").modal("show");
            	}
            } else {
            	//TODO: use modal popup
            	$(this).prop("disabled", false);
            	$(this).html("I Accept");
            	alert(acceptConsentResponseJson.errorMessage);
            }
        }
    });

}

function rejectConsentClickHandler() {
	console.log("rejectConsentClickHandler()");
	window.location.href = "/logout";
}

function registerUserClickHandler() {
    console.log("registerUserClickHandler()");

    var isValid = true;
    var errorMessage = "";

    if($("#registraionEmail").val() == "") {
        isValid = false;
        errorMessage += "Email is Required\r\n";
    }

    if($("#registrationPassword").val() == "") {
        isValid = false;
        errorMessage += "Password is Required\r\n";
    }

    if($("#registrationPassword").val() != $("#registrationConfirmPassword").val()) {
        isValid = false;
        errorMessage += "Passwords must match\r\n";
    }

    if(isValid) {
        $("#registerUser").prop("disabled", true);
    	$("#registerUser").html(
    	    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Processing...'
    	);

    	oktaSignIn.session.get(function (res) {
          // Session exists, show logged in state.
          if (res.status === 'ACTIVE') {
            // showApp()
            console.log("Session Active");
            oktaSignIn.session.close(function (err) {
              if (err) {
                // The user has not been logged out, perform some error handling here.
                console.log("Failed to close the session (if it exsists) otherwise fine");
                console.log(err);
              }
              // The user is now logged out.
                invokeRegisterBasic()
            });
          } else if (res.status === 'INACTIVE') {
            console.log("Session Not Active");
            invokeRegisterBasic();
          }
    	});
    } else {
        alert(errorMessage);
    }
}

function invokeRegisterBasic() {
    $.ajax({
        url: "/register-basic",
        type: "POST",
        data: JSON.stringify({"username": $("#registraionEmail").val(), "password": $("#registrationPassword").val()}),
        contentType: "application/json; charset=utf-8",
        success: data => {
            console.log(data);
            var acceptConsentResponseJson = JSON.parse(data);

            if(acceptConsentResponseJson.success) {
            	$("#basicRegistrationModal").modal("hide");
            	$("#basicRegistrationCompleteModal").modal("show");
            } else {
            	//TODO: use modal popup
            	errorMessage = acceptConsentResponseJson.errorMessage + "\r\n";

            	if(acceptConsentResponseJson.errorMessages != undefined){
            	    for(msgIdx in acceptConsentResponseJson.errorMessages) {
            	        errorMessage += acceptConsentResponseJson.errorMessages[msgIdx].errorMessage + "\r\n";
            	        if(acceptConsentResponseJson.errorMessages[msgIdx].errorMessage == "login: An object with this field already exists in the current organization") {
            	            $("#basicRegistrationModal").modal("hide");
            	            $("#popupLoginModal").modal("show");
            	            return;
            	        }
            	    }
            	}

            	alert(errorMessage);
            }
            $("#registerUser").prop("disabled", false);
        	$("#registerUser").html("Sign Me Up!");
        }
    });
}

function submitRegistrationDefaultClickHandler(){
    console.log("submitRegistrationDefaultClickHandler()");

    var isValid = true;
    var errorMessage = "";

    if($("#regDefaultFirstName").val() == "") {
        isValid = false;
        errorMessage += "First Name is Required\r\n";
    }

    if($("#regDefaultLastName").val() == "") {
        isValid = false;
        errorMessage += "Last Name is Required\r\n";
    }

    if($("#regDefaultHeight").val() == "") {
        isValid = false;
        errorMessage += "Height is Required\r\n";
    }

    if($("#regDefaultWeight").val() == "") {
        isValid = false;
        errorMessage += "Weight is Required\r\n";
    }

    if(isValid) {
        $("#submitRegistrationDefault").prop("disabled", true);
    	$("#submitRegistrationDefault").html(
    	    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Processing...'
    	);
    	var json_post_data = {
    	    "firstName": $("#regDefaultFirstName").val(),
    	    "lastName": $("#regDefaultLastName").val(),
    	    "dob": $("#regDefaultDOB").val(),
    	    "height": $("#regDefaultHeight").val(),
    	    "weight": $("#regDefaultWeight").val()
    	}
    	console.log(json_post_data);
        $.ajax({
            url: "/register-default",
            type: "POST",
            data: JSON.stringify(json_post_data),
            contentType: "application/json; charset=utf-8",
            success: data => {
                console.log(data);
                var responseJson = JSON.parse(data);

                if(responseJson.success) {
                	$("#userNameLabel").html(responseJson.user.profile.firstName + " " + responseJson.user.profile.lastName);
                	$("#registrationDefaultModal").modal("hide");
                	$("#finalRegistrationCompleteModal").modal("show");
                } else {
                	//TODO: use modal popup
                	errorMessage = responseJson.errorMessage + "\r\n";

                	if(responseJson.errorMessages != undefined){
                	    for(msgIdx in responseJson.errorMessages) {
                	        errorMessage += responseJson.errorMessages[msgIdx].errorMessage + "\r\n";
                	    }
                	}

                	alert(errorMessage);
                }
                $("#submitRegistrationDefault").prop("disabled", false);
            	$("#submitRegistrationDefault").html("Save");
            }
        });
    } else {
        alert(errorMessage);
    }
}

function submitRegistrationAlt1ClickHandler() {
    console.log("submitRegistrationAlt1()");

    var isValid = true;
    var errorMessage = "";

    if($("#regAlt1FirstName").val() == "") {
        isValid = false;
        errorMessage += "First Name is Required\r\n";
    }

    if($("#regAlt1LastName").val() == "") {
        isValid = false;
        errorMessage += "Last Name is Required\r\n";
    }

    if($("#regAlt1DOB").val() == "") {
        isValid = false;
        errorMessage += "Date of Birth is Required\r\n";
    }

    if($("#regAlt1MobileNumber").val() == "") {
        isValid = false;
        errorMessage += "Mobile Number is Required\r\n";
    }

    if(isValid) {
        $("#submitRegistrationAlt1").prop("disabled", true);
    	$("#submitRegistrationAlt1").html(
    	    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Processing...'
    	);
    	var json_post_data = {
    	    "firstName": $("#regAlt1FirstName").val(),
    	    "lastName": $("#regAlt1LastName").val(),
    	    "dob": $("#regAlt1DOB").val(),
    	    "mobilePhone": $("#regAlt1MobileNumber").val()
    	}
        $.ajax({
            url: "/register-alt1",
            type: "POST",
            data: JSON.stringify(json_post_data),
            contentType: "application/json; charset=utf-8",
            success: data => {
                console.log(data);
                var responseJson = JSON.parse(data);

                if(responseJson.success) {
                	$("#userNameLabel").html(responseJson.user.profile.firstName + " " + responseJson.user.profile.lastName);
                	$("#registrationAlt1Modal").modal("hide");
                	$("#finalRegistrationCompleteModal").modal("show");
                } else {
                	//TODO: use modal popup
                	errorMessage = responseJson.errorMessage + "\r\n";

                	if(responseJson.errorMessages != undefined){
                	    for(msgIdx in responseJson.errorMessages) {
                	        errorMessage += responseJson.errorMessages[msgIdx].errorMessage + "\r\n";
                	    }
                	}

                	alert(errorMessage);
                }
                $("#submitRegistrationAlt1").prop("disabled", false);
            	$("#submitRegistrationAlt1").html("Save");
            }
        });
    } else {
        alert(errorMessage);
    }
}

function verifyAccountClickHandler() {
    console.log("verifyAccountClickHandler()");

	var isValid = true;
    var errorMessage = "";

    if($("#verifyDOB").val() == "") {
        isValid = false;
        errorMessage += "Dateof Brith is Required\r\n";
    }

    if(isValid) {
        $("#verifyAccount").prop("disabled", true);
    	$("#verifyAccount").html(
    	    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Processing...'
    	);

    	var json_post_data = {
    	    "dob": $("#verifyDOB").val(),
    	    "stateToken": $("#stateToken").val()
    	}

        $.ajax({
            url: "/verify-dob",
            type: "POST",
            data: JSON.stringify(json_post_data),
            contentType: "application/json; charset=utf-8",
            success: data => {
                console.log(data);
                var responseJson = JSON.parse(data);

                if(responseJson.success) {
                	$("#verifyAccountModal").modal("hide");
                	$("#lblUserNamePreRegform").html(responseJson.user.profile.email);
                	$("#registrationPreRegModal").modal("show");
                } else {
                	//TODO: use modal popup
                	errorMessage = responseJson.errorMessage + "\r\n";

                	if(responseJson.errorMessages != undefined){
                	    for(msgIdx in responseJson.errorMessages) {
                	        errorMessage += responseJson.errorMessages[msgIdx].errorMessage + "\r\n";
                	    }
                	}

                	alert(errorMessage);
                }
                $("#verifyAccount").prop("disabled", false);
            	$("#verifyAccount").html("Verify");
            }
        });
    } else {
        alert(errorMessage);
    }
}



function verifyAccountClickHandler() {
    console.log("verifyAccountClickHandler()");

	var isValid = true;
    var errorMessage = "";

    if($("#verifyDOB").val() == "") {
        isValid = false;
        errorMessage += "Dateof Brith is Required\r\n";
    }

    if(isValid) {
        $("#verifyAccount").prop("disabled", true);
    	$("#verifyAccount").html(
    	    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Processing...'
    	);

    	var json_post_data = {
    	    "dob": $("#verifyDOB").val(),
    	    "stateToken": $("#stateToken").val()
    	}

        $.ajax({
            url: "/verify-dob",
            type: "POST",
            data: JSON.stringify(json_post_data),
            contentType: "application/json; charset=utf-8",
            success: data => {
                console.log(data);
                var responseJson = JSON.parse(data);

                if(responseJson.success) {
                	$("#verifyAccountModal").modal("hide");
                	$("#lblUserNamePreRegform").html(responseJson.user.profile.email);
                	$("#registrationPreRegModal").modal("show");
                } else {
                	//TODO: use modal popup
                	errorMessage = responseJson.errorMessage + "\r\n";

                	if(responseJson.errorMessages != undefined){
                	    for(msgIdx in responseJson.errorMessages) {
                	        errorMessage += responseJson.errorMessages[msgIdx].errorMessage + "\r\n";
                	    }
                	}

                	alert(errorMessage);
                }
                $("#verifyAccount").prop("disabled", false);
            	$("#verifyAccount").html("Verify");
            }
        });
    } else {
        alert(errorMessage);
    }
}



function setPreRegCredentialsClickHandler() {
    console.log("setPreRegCredentialsClickHandler()");

    var isValid = true;
    var errorMessage = "";

    if($("#preRegPassword").val() == "") {
        isValid = false;
        errorMessage += "Password is Required\r\n";
    }

    if($("#preRegPassword").val() != $("#preRegConfirmPassword").val()) {
        isValid = false;
        errorMessage += "Passwords must match\r\n";
    }

    if(isValid) {
        $("#setPreRegCredentials").prop("disabled", true);
    	$("#setPreRegCredentials").html(
    	    '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>Processing...'
    	);

    	var json_post_data = {
    	    "username": $("#lblUserNamePreRegform").html(),
    	    "newPassword": $("#preRegPassword").val(),
    	    "stateToken": $("#stateToken").val()
    	}

        $.ajax({
            url: "/pre-reg-password-set",
            type: "POST",
            data: JSON.stringify(json_post_data),
            contentType: "application/json; charset=utf-8",
            success: data => {
                console.log(data);
                var responseJson = JSON.parse(data);
                var txStatus = responseJson.status;

                if (txStatus == "SUCCESS") {
                	$("#registrationPreRegModal").modal("hide");
                	$("#finalRegistrationCompleteModal").modal("show");
                	$("#finalRegistrationCompleteModalClose").on("click", () => {
                	    window.location.href=responseJson.redirectUrl
                	});
                } else if (txStatus == "MFA_ENROLL") {
                    $("#registrationPreRegModal").modal("hide");
                    // show MFA enrollment modal
                    $("#stateToken").val(responseJson.stateToken);
                    var factors = responseJson._embedded.factors;
                    setupFactorEnrollmentList(factors);
                    $("#mfaEnrollmentModal").modal("show");
                }

                // if(responseJson.success) {
                // 	$("#registrationPreRegModal").modal("hide");
                // 	$("#finalRegistrationCompleteModal").modal("show");
                // 	$("#finalRegistrationCompleteModalClose").on("click", () => { window.location.href=responseJson.redirectUrl })
                // } else {
                // 	//TODO: use modal popup
                // 	errorMessage = responseJson.errorMessage + "\r\n";

                // 	if(responseJson.errorMessages != undefined){
                // 	    for(var msgIdx in responseJson.errorMessages) {
                // 	        errorMessage += responseJson.errorMessages[msgIdx].errorMessage + "\r\n";
                // 	    }
                // 	}

                // 	alert(errorMessage);
                // }
                $("#setPreRegCredentials").prop("disabled", false);
            	$("#setPreRegCredentials").html("Save");
            }
        });
    } else {
        alert(errorMessage);
    }
}