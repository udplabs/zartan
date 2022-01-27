// MFA enrollment event handlers
$("#_factorEnrollList").change(_factorEnrollListOnChange);
$("#_sendEnrollOTPButton").click(_sendEnrollOTPClickHandler);
$("#_mfaEnrollVerifyButton").click(_verifyEnrollOTPClickHandler);
$("#_mfaEnrollQuestionButton").click(_enrollQuestionClickHandler);
$("#_mfaFinishEnrollButton").click(_finishEnrollClickHandler);
$("#_mfaAddFactorButton").click(_mfaAddFactorClickHandler);
$("#_mfaFinishEnrollButton").hide();
_hideAllEnrollForms();

// click handlers for the add/delete buttons
$(".clickable.deleteable").click(_deleteFactorClickHandler);

function _deleteFactorClickHandler(event) {
    var user_id = $("#userId").val();
    var factor_id = $(this).data("id");
    var confirm_msg = "This operation cannot be undone.";
    console.log("Clicked delete icon with factor id " + factor_id);
    //event.preventDefault();

    if (confirm(confirm_msg)) {
        $.ajax({
            url: "/reset_factor/" + user_id + "/" + factor_id,
            type: "GET",
            contentType: "application/json; charset=utf-8",
            success: data => {
                //var response = JSON.parse(data);
                //console.log(response);
                location.reload();
            },
            error: function(xhr, status, error) {
                _logMessage("Status: " + status + ", message: " + error);
            }
        });
        return false;
    } else {
        return false;
    }
}

function _hideAllEnrollForms() {
    $("#_mfaEnrollPushForm").hide();
    $("#_mfaEnrollOTPForm").hide();
    $("#_mfaEnrollVerifyCodeForm").hide();
    $("#_mfaEnrollQuestionForm").hide();
    $("#_mfaEnrollQRCodeForm").hide();
    $("#_mfaEnrollWebAuthnForm").hide();

}

function _logMessage(message) {
    $("#_mfaStatusMessage").text(message);
}

function _logEnrollMessage(message) {
    $("#_mfaEnrollStatusMessage").text(message);
}

function _mfaAddFactorClickHandler() {
    var userId = $("#userId").val();
    _getAvailableFactors(userId);
}

function _getAvailableFactors(user_id) {
    $.ajax({
        url: "/get_available_factors/" + user_id,
        type: "GET",
        contentType: "application/json; charset=utf-8",
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            _setupFactorList(response);
            $("#_mfaEnrollmentModal").modal("show");
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _setupFactorList(factors) {
    $("#_factorEnrollList").empty().append("<option>Select Factor</option>");

    // make a list of factors to choose from, and also map
    // to friendly display names
    var factors_array = [];
    for (var factorIdx in factors) {
        var factor = factors[factorIdx];
        var factorType = factor.factorType;
        var provider = factor.provider;
        // default to factorType as the name as a fallback
        var factorName = factorType;
        var sortOrder = 100;
        console.log(factorType);
        console.log(provider);

        if (factorType == "token:software:totp") {
            if (provider == "GOOGLE") {
                factor.factorName = "Google Authenticator";
                factor.sortOrder = 20;
            }
            else if (provider == "OKTA") {
                // don't list Okta Verify OTP
                continue;
            }
        }
        else if (factorType == "push") {
            factor.factorName = "Okta Verify";
            factor.sortOrder = 10;
        }
        else if (factorType == "sms") {
            factor.factorName = "SMS";
            factor.sortOrder = 30;
        }
        else if (factorType == "call") {
            factor.factorName = "Voice Call";
            factor.sortOrder = 40;
        }
        else if (factorType == "question") {
            factor.factorName = "Security Question";
            factor.sortOrder = 50;
        }
        else if (factorType == "webauthn") {
            factor.factorName = "Web Authn";
            factor.sortOrder = 60;
        }
        else
        {
             continue;
        }

        factors_array.push(factor);
    }

    // now add the sorted array to the select list
    factors_array.sort(function(a, b) {
        return a.sortOrder - b.sortOrder;
    });

    for (var i = 0; i < factors_array.length; i++) {
        var factor = factors_array[i];
        var option = '<option value="' + factor.factorName;
        option += '" data-type="' + factor.factorType + '"';
        option += '" data-provider="' + factor.provider + '"';
        option += '" data-phone="' + factor.phoneNumber + '"';
        option += '>' + factor.factorName + '</option>';
        $("#_factorEnrollList").append(option);
    }
}

function _factorEnrollListOnChange() {
    _hideAllEnrollForms();
    _logEnrollMessage("");
    var factorName = $("#_factorEnrollList option:selected").text();
    var factorType = $("#_factorEnrollList option:selected").data("type");
    var provider = $("#_factorEnrollList option:selected").data("provider");
    var phoneNumber = $("#_factorEnrollList option:selected").data("phone");

    $("#_mfaFactorName").val(factorName);
    $("#_mfaFactorType").val(factorType);
    $("#_mfaProvider").val(provider);

    switch (factorName) {
        case "Okta Verify":
        case "Okta Verify Push":
            _enrollPushFactor();
            break;
        case "Google Authenticator":
            $("#_mfaEnrollVerifyCodeForm").show();
            _enrollTOTPFactor();
            $("#_mfaEnrollPassCode").focus();
            break;
        case "SMS":
            $("#_mfaEnrollOTPForm").show();
            $("#_sendEnrollOTPButton").text("Send SMS");
            $("#_mfaEnrollRecipient").val(phoneNumber);
            $("#_mfaEnrollRecipient").focus();
            break;
        case "Voice Call":
            $("#_mfaEnrollOTPForm").show();
            $("#_sendEnrollOTPButton").text("Call Me");
            $("#_mfaEnrollRecipient").val(phoneNumber);
            $("#_mfaEnrollRecipient").focus();
            break;
        case "Security Question":
            _getAvailableQuestions();
            $("#_mfaEnrollQuestionForm").show();
            break;
        case "Web Authn":
            _enrollWebAuthn();
            $("#_mfaEnrollWebAuthnForm").show();
            break;
    }
}

function _enrollPushFactor() {
    var user_id = $("#userId").val();
    var factorType = $("#_mfaFactorType").val();
    var provider = $("#_mfaProvider").val();
    var payload = {
        "user_id": user_id,
        "factor_type": factorType,
        "provider": provider
    };

    $.ajax({
        url: "/enroll_push",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            var factorId = response.id;
            var qrCode = response._embedded.activation._links.qrcode.href;
            $("#_mfaFactorID").val(factorId);
            $("#_mfaEnrollQRCode").attr("src", qrCode);
            $("#_mfaEnrollQRCodeForm").show();

            // start polling for a response
            setTimeout(_pollForPushEnrollment, 3000);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _enrollWebAuthn() {
    var user_id = $("#userId").val();
    var factorType = $("#_mfaFactorType").val();
    var provider = $("#_mfaProvider").val();
    var payload = {
        "user_id": user_id,
        "factor_type": factorType,
        "provider": provider
    };

    $.ajax({
        url: "/enroll_webauthn",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var webauthnresponse = JSON.parse(data);
            console.log(webauthnresponse);
            $("#_mfaWebAuthnResponse").val(data);
        },
        error: function(xhr, status, error) {
            logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _pollForPushEnrollment() {
    var user_id = $("#userId").val();
    var factor_id = $("#_mfaFactorID").val();
    var factor_name = $("#_mfaFactorName").val();
    var payload = {
        "user_id": user_id,
        "factor_id": factor_id
    };

    $.ajax({
        url: "/poll_for_push_enrollment",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            if (response.status == "ACTIVE") {
                $(".overlay-effect").removeClass("hidden").addClass("visible");
                _logEnrollMessage(factor_name + " successfully enrolled!");
                //$("#_mfaEnrollQRCodeForm").hide();
                _finishEnrollment();
            } else if (response.factorResult == "WAITING") {
                _logEnrollMessage("Waiting for enrollment");
                setTimeout(_pollForPushEnrollment, 3000);
            } else if (response.factorResult == "TIMEOUT") {
                _logEnrollMessage("Your push notification has timed out");
                $("#_sendPushButton").text("Resend Push");
                $("#_sendPushButton").click(_resendPushClickHandler);
            }
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _resendPushClickHandler() {
    var user_id = $("#userId").val();
    var factor_id = $("#_mfaFactorID").val();
    var state_token = $("#_mfaStateToken").val();
    _logMessage("Push notification re-sent");
    var payload = {
        "user_id": user_id,
        "factor_id": factor_id
    };

    $.ajax({
        url: "/resend_push",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            // set up the polling
            setTimeout(_pollForPushEnrollment, 3000);
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _enrollTOTPFactor() {
    var user_id = $("#userId").val();
    var factorType = $("#_mfaFactorType").val();
    var provider = $("#_mfaProvider").val();
    var payload = {
        "user_id": user_id,
        "factor_type": factorType,
        "provider": provider
    };

    $.ajax({
        url: "/enroll_totp",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            var factorId = response.id;
            var qrCode = response._embedded.activation._links.qrcode.href;
            $("#_mfaFactorID").val(factorId);
            $("#_mfaEnrollQRCode").attr("src", qrCode);
            $("#_mfaEnrollQRCodeForm").show();
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

// for SMS and voice
function _sendEnrollOTPClickHandler() {
    var user_id = $("#userId").val();
    var factorType = $("#_mfaFactorType").val();
    var provider = $("#_mfaProvider").val();
    var phoneNumber = $("#_mfaEnrollRecipient").val();
    var payload = {
        "user_id": user_id,
        "factor_type": factorType,
        "provider": provider,
        "phone_number": phoneNumber
    };

    $.ajax({
        url: "/enroll_sms_voice",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            var txStatus = response.status;

            if (txStatus == "PENDING_ACTIVATION") {
                var factorId = response.id;
                $("#_mfaFactorID").val(factorId);
                $("#_mfaEnrollVerifyCodeForm").show();
                $("#_mfaEnrollPassCode").focus();
                _logEnrollMessage("A code has been sent to your device");
            } else if (txStatus == "ACTIVE") {
                // this factor is already using a verified phone number,
                // so just let the user know it's been reactivated
                var message = "Your phone number was previously verified, ";
                message += "so it's been reactivated for MFA";
                _logEnrollMessage(message);
                $("#_mfaEnrollVerifyCodeForm").hide();
                _finishEnrollment();
            }
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _verifyEnrollOTPClickHandler() {
    var user_id = $("#userId").val();
    var factorId = $("#_mfaFactorID").val();
    var pass_code = $("#_mfaEnrollPassCode").val();
    var factor_name = $("#_mfaFactorName").val();
    var payload = {
        "user_id": user_id,
        "factor_id": factorId,
        "pass_code": pass_code
    };

    $.ajax({
        url: "/activate_totp",
        type: "POST",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify(payload),
        success: data => {
            var response = JSON.parse(data);
            console.log(response);
            if (response.errorCode) {
                _logEnrollMessage(response.errorSummary);
            } else if (response.status == "ACTIVE") {
                _logEnrollMessage(factor_name + " successfully enrolled!");
                $("#_mfaEnrollPassCode").val("");
                $("#_mfaEnrollQRCodeForm").hide();
                $("#_mfaEnrollVerifyCodeForm").hide();
                _finishEnrollment();
            }
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _enrollQuestionClickHandler() {
    var user_id = $("#userId").val();
    var factor_name = $("#_mfaFactorName").val();
    var factorType = $("#_mfaFactorType").val();
    var provider = $("#_mfaProvider").val();
    var question = $("#_mfaEnrollQuestion").val();
    var answer = $("#_mfaEnrollAnswer").val();
    var payload = {
        "user_id": user_id,
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
            var response = JSON.parse(data);
            console.log(response);
            if (response.status == "ACTIVE") {
                _logEnrollMessage(factor_name + " successfully enrolled!");
                $("#_mfaEnrollQuestionForm").hide();
                _finishEnrollment();
            }
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _getAvailableQuestions() {
    var user_id = $("#userId").val();
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
            _setupQuestionList(response);
        },
        error: function(xhr, status, error) {
            _logMessage("Status: " + status + ", message: " + error);
        }
    });
}

function _setupQuestionList(questions) {
    $("#_mfaEnrollQuestion").empty();
    for (var qIdx in questions) {
        var q = questions[qIdx];
        var value = q.question;
        var label = q.questionText;
        var option = new Option(label, value);
        //console.log("Adding question " + label + " wth value " + value);
        $("#_mfaEnrollQuestion").append(option);
    }
    // and add the custom question option to the end of the list
    //$("#_mfaEnrollQuestion").append(new Option("Create your own security question", "custom"));
}

function _finishEnrollment() {
    console.log("_finishEnrollment");
    $("#_mfaFinishEnrollButton").show();
    setTimeout(_logEnrollMessage, 5000);
}

function _finishEnrollClickHandler() {
    console.log("Enrollment finished");
    location.reload();
}