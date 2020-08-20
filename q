[1mdiff --git a/GlobalBehaviorandComponents/templates/components/template-login-widget.html b/GlobalBehaviorandComponents/templates/components/template-login-widget.html[m
[1mindex 6161877..e7d5386 100644[m
[1m--- a/GlobalBehaviorandComponents/templates/components/template-login-widget.html[m
[1m+++ b/GlobalBehaviorandComponents/templates/components/template-login-widget.html[m
[36m@@ -2,6 +2,42 @@[m
     <section class="main-container">[m
         <div class="container" >[m
            <div class="row">[m
[32m+[m[32m             <div class="dropdown col-md-12 text-right">[m
[32m+[m[32m                <button class="btn btn-primary rounded-pill dropdown-toggle" id="language" type="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Select a Language</button>[m
[32m+[m[32m                <style>[m
[32m+[m[32m                  .dropdown-item {[m
[32m+[m[32m                        font-size: 11px;[m
[32m+[m[32m                  }[m
[32m+[m[32m                </style>[m
[32m+[m[32m                <div class="dropdown-menu" aria-labelledby="dropdownMenuButton">[m
[32m+[m[32m                    <a class="dropdown-item" href="#" onclick="changelanguage('cs')">Czech</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('da')">Danish</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('de')">German</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('el')">Greek</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('en')">English</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('es')">Spanish</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('fi')">Finnish</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('fr')">French</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('hu')">Hungarian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('id')">Indonesian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('it')">Italian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('ja')">Japanese</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('ko')">Korean</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('ms')">Malaysian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('nb')">Norwegian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('nl-NL')">Dutch</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('pl')">Polish</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('pt-BR')">Portuguese (Brazil)</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('ro')">Romanian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('ru')">Russian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('sv')">Swedish</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('th')">Thai</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('tr')">Turkish</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('zh-TW')">Ukrainian</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('zh-CN)">Chinese (PRC)</a>[m
[32m+[m[32m                    <a value="press" class="dropdown-item" href="#" onclick="changelanguage('zh-TW')">Chinese (Taiwan)</a>[m
[32m+[m[32m                </div>[m
[32m+[m[32m            </div>[m
             <div class="col-md-8 offset-md-2">[m
             <!-- main start -->[m
             <!-- ================ -->[m
[36m@@ -52,13 +88,28 @@[m
                     }[m
 [m
                   </style>[m
[32m+[m[32m                  <script>[m
[32m+[m[32m                  function changelanguage(lang){[m
[32m+[m[32m                    $("#language").val(lang);[m
[32m+[m[32m                    console.log(signInWidget);[m
[32m+[m[32m                    signInWidget.remove();[m
[32m+[m[32m                    signInWidget.renderEl({el: '#sign-in-widget'});[m
[32m+[m[32m                  }[m
[32m+[m[32m                  </script>[m
[32m+[m[32m                  <input name="language" id="language" class="form-control" type="hidden" value="en">[m
[32m+[m[41m                  [m
                   <div id="sign-in-widget"></div>[m
                   <script type="text/javascript">[m
[31m-                    new OktaSignIn({[m
[32m+[m[32m                   signInWidgetConfig = {[m
                       baseUrl: "{{config.okta_org_name}}",[m
                       logo: "{{config.settings.app_logo}}",[m
                       clientId: "{{config.client_id}}",[m
                       redirectUri: "{{config.redirect_uri}}",[m
[32m+[m[32m                      language: function () {[m
[32m+[m[32m                        newlang = $("#language").val();[m
[32m+[m[32m                        console.log(newlang);[m
[32m+[m[32m                        return newlang;[m
[32m+[m[32m                      },[m
                       i18n: {[m
                         en: {[m
                           'primaryauth.title': 'Sign in to {{config.settings.app_name}}'[m
[36m@@ -127,15 +178,16 @@[m
                             return nname;[m
                           }[m
                       },[m
[31m-                    }).renderEl([m
[31m-                      { el: '#sign-in-widget' },[m
[31m-                      function (res) {}[m
[31m-                    );[m
[32m+[m[32m                    };[m
[32m+[m
[32m+[m[32m                    signInWidget = new OktaSignIn(signInWidgetConfig);[m
[32m+[m[32m                    signInWidget.renderEl({el: '#sign-in-widget'});[m
                   </script>[m
                 </div>[m
               </div>[m
             </div>[m
             </div>[m
         </div>[m
[32m+[m
     </section>[m
     <!-- page-wrapper end -->[m
\ No newline at end of file[m
[1mdiff --git a/_consumerproducts/templates/consumerproducts/discounts.html b/_consumerproducts/templates/consumerproducts/discounts.html[m
[1mnew file mode 100644[m
[1mindex 0000000..ad3b2f1[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/templates/consumerproducts/discounts.html[m
[36m@@ -0,0 +1,467 @@[m
[32m+[m[32m{% extends "consumerproducts/template.html" %}[m
[32m+[m
[32m+[m[32m{% block content %}[m
[32m+[m[32m <section class="bg-light py-5">[m
[32m+[m[32m    <div class="container">[m
[32m+[m[32m        <div class="row">[m
[32m+[m[32m            <div class="col-md-12">[m
[32m+[m[32m                <div class="card border-bottom">[m
[32m+[m[32m                    <div class="card-header">Download Savings Today</div>[m
[32m+[m[32m                        <div class="card-body">[m
[32m+[m[32m                            <style>[m
[32m+[m[32m                                .checkbox1 {[m
[32m+[m[32m                                    display: inline-block;[m
[32m+[m[32m                                    content: '';[m
[32m+[m[32m                                    width: 20px;[m
[32m+[m[32m                                    height: 20px;[m
[32m+[m[32m                                    border: 0.88px solid #979797;[m
[32m+[m[32m                                    border-radius: 3px;[m
[32m+[m[32m                                    background-color: #ffffff;[m
[32m+[m[32m                                    border-radius: 2px;[m
[32m+[m[32m                                    vertical-align: middle;[m
[32m+[m[32m                                }[m
[32m+[m[32m                                .coupon {[m
[32m+[m[32m                                    display: inline;[m
[32m+[m[32m                                    height: 20px;[m
[32m+[m[32m                                    color: #00205B;[m
[32m+[m[32m                                    font-family: "Gotham Rounded Medium", sans-serif;[m
[32m+[m[32m                                    font-size: 40px;[m
[32m+[m[32m                                    font-weight: 500;[m
[32m+[m[32m                                    vertical-align: sub;[m
[32m+[m[32m                                    /* text-align: center; */[m
[32m+[m[32m                                    margin-left: 10px;[m
[32m+[m[32m                                    background: transparent;[m
[32m+[m[32m                                    padding: 0;[m
[32m+[m[32m                                }[m
[32m+[m
[32m+[m[32m                            </style>[m
[32m+[m[32m                            <h4>Please select coupons to print.</h4><br>[m
[32m+[m	[32m                        <button class="btn btn-primary" type="button" id="buttonPrint">Select All</button>[m
[32m+[m	[32m                        <button class="btn btn-primary" type="button" id="buttonPrint">Deselect All</button>[m
[32m+[m	[32m                        <button class="btn btn-primary" style="float:right;" type="button" onclick="moreinfo()" id="buttonPrint">Print Coupons</button>[m
[32m+[m	[32m                        <br><br>[m
[32m+[m	[32m                        <hr>[m
[32m+[m[32m                            <h1>U by Kotex®</h1>[m
[32m+[m[41m                        [m	[32m<div class="bg-light" style="padding: 20 20 20 20; ">[m
[32m+[m[41m                        [m	[32m    <div style="width: 300px;">[m
[32m+[m[32m                                <img  border="0" src="//d2aiu90bsqeeag.cloudfront.net/creative/viewPreprint?programId=103941473&amp;merchantId=11613065&amp;affiliateId=12832277&amp;viewType=viewFull"><br>[m
[32m+[m[32m                                <input type="checkbox" class="checkbox1"><label class="coupon">Save $0.50</label><br>[m
[32m+[m[41m                            [m	[32mon any ONE (1) package of U by Kotex® Products[m
[32m+[m[32m                                <br>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                            <br><br>[m
[32m+[m[32m                            <h1>GoodNites®</h1>[m
[32m+[m[41m                        [m	[32m<div class="bg-light" style="padding: 20 20 20 20; ">[m
[32m+[m[41m                        [m	[32m    <div style="width: 300px;display: inline-block;">[m
[32m+[m[32m                                    <img  border="0" src="//d2aiu90bsqeeag.cloudfront.net/creative/viewPreprint?programId=103941839&amp;merchantId=11613065&amp;affiliateId=12832277&amp;viewType=viewFull"><br>[m
[32m+[m[32m                                    <input type="checkbox" class="checkbox1"><label class="coupon">Get $1.50 Off</label>[m
[32m+[m[41m                            [m	[32m    any ONE (1) package of Goodnites® Bed Mats[m
[32m+[m[32m                                    <br>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                                <div style="width: 300px;display: inline-block;">[m
[32m+[m[32m                                    <img  border="0" src="//d2aiu90bsqeeag.cloudfront.net/creative/viewPreprint?programId=103941810&amp;merchantId=11613065&amp;affiliateId=12832277&amp;viewType=viewFull"><br>[m
[32m+[m[32m                                    <input type="checkbox" class="checkbox1"><label class="coupon">Get $1.50 Off</label>[m
[32m+[m[41m                            [m	[32m    any ONE (1) package of Goodnites® Bedtime Pants[m
[32m+[m[32m                                    <br>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                            <br><br>[m
[32m+[m[32m                            <h1>Huggies®</h1>[m
[32m+[m[41m                        [m	[32m<div class="bg-light" style="padding: 20 20 20 20; ">[m
[32m+[m[41m                        [m	[32m    <div style="width: 300px;display: inline-block;">[m
[32m+[m[32m                                    <img  border="0" src="//d2aiu90bsqeeag.cloudfront.net/creative/viewPreprint?programId=103941551&amp;merchantId=11613065&amp;affiliateId=12832277&amp;viewType=viewFull"><br>[m
[32m+[m[32m                                    <input type="checkbox" class="checkbox1"><label class="coupon">Get $1.00 Off</label>[m
[32m+[m[41m                                [m	[32many TWO (2) packages of Huggies® Wipes[m
[32m+[m[32m                                    <br>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                                <div style="width: 300px;display: inline-block;">[m
[32m+[m[32m                                    <img  border="0" src="//d2aiu90bsqeeag.cloudfront.net/creative/viewPreprint?programId=103941521&amp;merchantId=11613065&amp;affiliateId=12832277&amp;viewType=viewFull"><br>[m
[32m+[m[32m                                    <input type="checkbox" class="checkbox1"><label class="coupon">Get $1.00 Off</label>[m
[32m+[m[41m                            [m	[32m    any ONE (1) package of Huggies® Diapers[m
[32m+[m[32m                                    <br>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                </div>[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</section>[m
[32m+[m
[32m+[m[32m<div class="modal fade" id="moreinfo" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">[m
[32m+[m[32m    <div class="modal-dialog modal-dialog-centered" role="document">[m
[32m+[m[32m        <div class="modal-content">[m
[32m+[m[32m                <div class="modal-header">[m
[32m+[m[32m                    <h1 class="modal-title" id="exampleModalCenterTitle">Tell Us About Yourself!</h1><br>[m
[32m+[m[32m                </div>[m
[32m+[m[32m                <div class="modal-body" id="mfamodalbody">[m
[32m+[m[32m                    <form class="form-horizontal" action='updateprofile' method="POST">[m
[32m+[m[32m                        <h3>Gender</h3>[m
[32m+[m[32m                        <div class="custom-control custom-radio custom-control-solid">[m
[32m+[m[32m                            <input class="custom-control-input" id="customRadioSolid1" type="radio" value="Male" name="gender">[m
[32m+[m[32m                            <label class="custom-control-label" for="customRadioSolid1">Male</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="custom-control custom-radio custom-control-solid">[m
[32m+[m[32m                            <input class="custom-control-input" id="customRadioSolid2" type="radio" value="Female" name="gender">[m
[32m+[m[32m                            <label class="custom-control-label" for="customRadioSolid2">Female</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <br>[m
[32m+[m[32m                        <script src="https://unpkg.com/bootstrap-datepicker@1.9.0/dist/js/bootstrap-datepicker.min.js"></script>[m
[32m+[m[32m                        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-datepicker/1.4.1/css/bootstrap-datepicker3.css">[m
[32m+[m[32m                        <h3>Birthdate</h3>[m
[32m+[m[32m                        <input type="text" class="form-control" name="dob" id="dob"><br>[m
[32m+[m[32m                        <script>[m
[32m+[m[32m                            $('#dob').datepicker({[m
[32m+[m[32m                                autoclose: true[m
[32m+[m[32m                            });[m
[32m+[m[32m                        </script>[m
[32m+[m[32m                        <h3>Country</h3>[m
[32m+[m[32m                        <select id="country" class="form-control" name="country">[m
[32m+[m[32m                            <option value="US">United States</option>[m
[32m+[m[32m                            <option value="GB">United Kingdom</option>[m
[32m+[m[32m                            <option value="AF">Afghanistan</option>[m
[32m+[m[41m                        [m	[32m<option value="AX">Åland Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="AL">Albania</option>[m
[32m+[m[41m                        [m	[32m<option value="DZ">Algeria</option>[m
[32m+[m[41m                        [m	[32m<option value="AS">American Samoa</option>[m
[32m+[m[41m                        [m	[32m<option value="AD">Andorra</option>[m
[32m+[m[41m                        [m	[32m<option value="AO">Angola</option>[m
[32m+[m[41m                        [m	[32m<option value="AI">Anguilla</option>[m
[32m+[m[41m                        [m	[32m<option value="AQ">Antarctica</option>[m
[32m+[m[41m                        [m	[32m<option value="AG">Antigua and Barbuda</option>[m
[32m+[m[41m                        [m	[32m<option value="AR">Argentina</option>[m
[32m+[m[41m                        [m	[32m<option value="AM">Armenia</option>[m
[32m+[m[41m                        [m	[32m<option value="AW">Aruba</option>[m
[32m+[m[41m                        [m	[32m<option value="AU">Australia</option>[m
[32m+[m[41m                        [m	[32m<option value="AT">Austria</option>[m
[32m+[m[41m                        [m	[32m<option value="AZ">Azerbaijan</option>[m
[32m+[m[41m                        [m	[32m<option value="BS">Bahamas</option>[m
[32m+[m[41m                        [m	[32m<option value="BH">Bahrain</option>[m
[32m+[m[41m                        [m	[32m<option value="BD">Bangladesh</option>[m
[32m+[m[41m                        [m	[32m<option value="BB">Barbados</option>[m
[32m+[m[41m                        [m	[32m<option value="BY">Belarus</option>[m
[32m+[m[41m                        [m	[32m<option value="BE">Belgium</option>[m
[32m+[m[41m                        [m	[32m<option value="BZ">Belize</option>[m
[32m+[m[41m                        [m	[32m<option value="BJ">Benin</option>[m
[32m+[m[41m                        [m	[32m<option value="BM">Bermuda</option>[m
[32m+[m[41m                        [m	[32m<option value="BT">Bhutan</option>[m
[32m+[m[41m                        [m	[32m<option value="BO">Bolivia, Plurinational State of</option>[m
[32m+[m[41m                        [m	[32m<option value="BQ">Bonaire, Sint Eustatius and Saba</option>[m
[32m+[m[41m                        [m	[32m<option value="BA">Bosnia and Herzegovina</option>[m
[32m+[m[41m                        [m	[32m<option value="BW">Botswana</option>[m
[32m+[m[41m                        [m	[32m<option value="BV">Bouvet Island</option>[m
[32m+[m[41m                        [m	[32m<option value="BR">Brazil</option>[m
[32m+[m[41m                        [m	[32m<option value="IO">British Indian Ocean Territory</option>[m
[32m+[m[41m                        [m	[32m<option value="BN">Brunei Darussalam</option>[m
[32m+[m[41m                        [m	[32m<option value="BG">Bulgaria</option>[m
[32m+[m[41m                        [m	[32m<option value="BF">Burkina Faso</option>[m
[32m+[m[41m                        [m	[32m<option value="BI">Burundi</option>[m
[32m+[m[41m                        [m	[32m<option value="KH">Cambodia</option>[m
[32m+[m[41m                        [m	[32m<option value="CM">Cameroon</option>[m
[32m+[m[41m                        [m	[32m<option value="CA">Canada</option>[m
[32m+[m[41m                        [m	[32m<option value="CV">Cape Verde</option>[m
[32m+[m[41m                        [m	[32m<option value="KY">Cayman Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="CF">Central African Republic</option>[m
[32m+[m[41m                        [m	[32m<option value="TD">Chad</option>[m
[32m+[m[41m                        [m	[32m<option value="CL">Chile</option>[m
[32m+[m[41m                        [m	[32m<option value="CN">China</option>[m
[32m+[m[41m                        [m	[32m<option value="CX">Christmas Island</option>[m
[32m+[m[41m                        [m	[32m<option value="CC">Cocos (Keeling) Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="CO">Colombia</option>[m
[32m+[m[41m                        [m	[32m<option value="KM">Comoros</option>[m
[32m+[m[41m                        [m	[32m<option value="CG">Congo</option>[m
[32m+[m[41m                        [m	[32m<option value="CD">Congo, the Democratic Republic of the</option>[m
[32m+[m[41m                        [m	[32m<option value="CK">Cook Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="CR">Costa Rica</option>[m
[32m+[m[41m                        [m	[32m<option value="CI">Côte d'Ivoire</option>[m
[32m+[m[41m                        [m	[32m<option value="HR">Croatia</option>[m
[32m+[m[41m                        [m	[32m<option value="CU">Cuba</option>[m
[32m+[m[41m                        [m	[32m<option value="CW">Curaçao</option>[m
[32m+[m[41m                        [m	[32m<option value="CY">Cyprus</option>[m
[32m+[m[41m                        [m	[32m<option value="CZ">Czech Republic</option>[m
[32m+[m[41m                        [m	[32m<option value="DK">Denmark</option>[m
[32m+[m[41m                        [m	[32m<option value="DJ">Djibouti</option>[m
[32m+[m[41m                        [m	[32m<option value="DM">Dominica</option>[m
[32m+[m[41m                        [m	[32m<option value="DO">Dominican Republic</option>[m
[32m+[m[41m                        [m	[32m<option value="EC">Ecuador</option>[m
[32m+[m[41m                        [m	[32m<option value="EG">Egypt</option>[m
[32m+[m[41m                        [m	[32m<option value="SV">El Salvador</option>[m
[32m+[m[41m                        [m	[32m<option value="GQ">Equatorial Guinea</option>[m
[32m+[m[41m                        [m	[32m<option value="ER">Eritrea</option>[m
[32m+[m[41m                        [m	[32m<option value="EE">Estonia</option>[m
[32m+[m[41m                        [m	[32m<option value="ET">Ethiopia</option>[m
[32m+[m[41m                        [m	[32m<option value="FK">Falkland Islands (Malvinas)</option>[m
[32m+[m[41m                        [m	[32m<option value="FO">Faroe Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="FJ">Fiji</option>[m
[32m+[m[41m                        [m	[32m<option value="FI">Finland</option>[m
[32m+[m[41m                        [m	[32m<option value="FR">France</option>[m
[32m+[m[41m                        [m	[32m<option value="GF">French Guiana</option>[m
[32m+[m[41m                        [m	[32m<option value="PF">French Polynesia</option>[m
[32m+[m[41m                        [m	[32m<option value="TF">French Southern Territories</option>[m
[32m+[m[41m                        [m	[32m<option value="GA">Gabon</option>[m
[32m+[m[41m                        [m	[32m<option value="GM">Gambia</option>[m
[32m+[m[41m                        [m	[32m<option value="GE">Georgia</option>[m
[32m+[m[41m                        [m	[32m<option value="DE">Germany</option>[m
[32m+[m[41m                        [m	[32m<option value="GH">Ghana</option>[m
[32m+[m[41m                        [m	[32m<option value="GI">Gibraltar</option>[m
[32m+[m[41m                        [m	[32m<option value="GR">Greece</option>[m
[32m+[m[41m                        [m	[32m<option value="GL">Greenland</option>[m
[32m+[m[41m                        [m	[32m<option value="GD">Grenada</option>[m
[32m+[m[41m                        [m	[32m<option value="GP">Guadeloupe</option>[m
[32m+[m[41m                        [m	[32m<option value="GU">Guam</option>[m
[32m+[m[41m                        [m	[32m<option value="GT">Guatemala</option>[m
[32m+[m[41m                        [m	[32m<option value="GG">Guernsey</option>[m
[32m+[m[41m                        [m	[32m<option value="GN">Guinea</option>[m
[32m+[m[41m                        [m	[32m<option value="GW">Guinea-Bissau</option>[m
[32m+[m[41m                        [m	[32m<option value="GY">Guyana</option>[m
[32m+[m[41m                        [m	[32m<option value="HT">Haiti</option>[m
[32m+[m[41m                        [m	[32m<option value="HM">Heard Island and McDonald Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="VA">Holy See (Vatican City State)</option>[m
[32m+[m[41m                        [m	[32m<option value="HN">Honduras</option>[m
[32m+[m[41m                        [m	[32m<option value="HK">Hong Kong</option>[m
[32m+[m[41m                        [m	[32m<option value="HU">Hungary</option>[m
[32m+[m[41m                        [m	[32m<option value="IS">Iceland</option>[m
[32m+[m[41m                        [m	[32m<option value="IN">India</option>[m
[32m+[m[41m                        [m	[32m<option value="ID">Indonesia</option>[m
[32m+[m[41m                        [m	[32m<option value="IR">Iran, Islamic Republic of</option>[m
[32m+[m[41m                        [m	[32m<option value="IQ">Iraq</option>[m
[32m+[m[41m                        [m	[32m<option value="IE">Ireland</option>[m
[32m+[m[41m                        [m	[32m<option value="IM">Isle of Man</option>[m
[32m+[m[41m                        [m	[32m<option value="IL">Israel</option>[m
[32m+[m[41m                        [m	[32m<option value="IT">Italy</option>[m
[32m+[m[41m                        [m	[32m<option value="JM">Jamaica</option>[m
[32m+[m[41m                        [m	[32m<option value="JP">Japan</option>[m
[32m+[m[41m                        [m	[32m<option value="JE">Jersey</option>[m
[32m+[m[41m                        [m	[32m<option value="JO">Jordan</option>[m
[32m+[m[41m                        [m	[32m<option value="KZ">Kazakhstan</option>[m
[32m+[m[41m                        [m	[32m<option value="KE">Kenya</option>[m
[32m+[m[41m                        [m	[32m<option value="KI">Kiribati</option>[m
[32m+[m[41m                        [m	[32m<option value="KP">Korea, Democratic People's Republic of</option>[m
[32m+[m[41m                        [m	[32m<option value="KR">Korea, Republic of</option>[m
[32m+[m[41m                        [m	[32m<option value="KW">Kuwait</option>[m
[32m+[m[41m                        [m	[32m<option value="KG">Kyrgyzstan</option>[m
[32m+[m[41m                        [m	[32m<option value="LA">Lao People's Democratic Republic</option>[m
[32m+[m[41m                        [m	[32m<option value="LV">Latvia</option>[m
[32m+[m[41m                        [m	[32m<option value="LB">Lebanon</option>[m
[32m+[m[41m                        [m	[32m<option value="LS">Lesotho</option>[m
[32m+[m[41m                        [m	[32m<option value="LR">Liberia</option>[m
[32m+[m[41m                        [m	[32m<option value="LY">Libya</option>[m
[32m+[m[41m                        [m	[32m<option value="LI">Liechtenstein</option>[m
[32m+[m[41m                        [m	[32m<option value="LT">Lithuania</option>[m
[32m+[m[41m                        [m	[32m<option value="LU">Luxembourg</option>[m
[32m+[m[41m                        [m	[32m<option value="MO">Macao</option>[m
[32m+[m[41m                        [m	[32m<option value="MK">Macedonia, the former Yugoslav Republic of</option>[m
[32m+[m[41m                        [m	[32m<option value="MG">Madagascar</option>[m
[32m+[m[41m                        [m	[32m<option value="MW">Malawi</option>[m
[32m+[m[41m                        [m	[32m<option value="MY">Malaysia</option>[m
[32m+[m[41m                        [m	[32m<option value="MV">Maldives</option>[m
[32m+[m[41m                        [m	[32m<option value="ML">Mali</option>[m
[32m+[m[41m                        [m	[32m<option value="MT">Malta</option>[m
[32m+[m[41m                        [m	[32m<option value="MH">Marshall Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="MQ">Martinique</option>[m
[32m+[m[41m                        [m	[32m<option value="MR">Mauritania</option>[m
[32m+[m[41m                        [m	[32m<option value="MU">Mauritius</option>[m
[32m+[m[41m                        [m	[32m<option value="YT">Mayotte</option>[m
[32m+[m[41m                        [m	[32m<option value="MX">Mexico</option>[m
[32m+[m[41m                        [m	[32m<option value="FM">Micronesia, Federated States of</option>[m
[32m+[m[41m                        [m	[32m<option value="MD">Moldova, Republic of</option>[m
[32m+[m[41m                        [m	[32m<option value="MC">Monaco</option>[m
[32m+[m[41m                        [m	[32m<option value="MN">Mongolia</option>[m
[32m+[m[41m                        [m	[32m<option value="ME">Montenegro</option>[m
[32m+[m[41m                        [m	[32m<option value="MS">Montserrat</option>[m
[32m+[m[41m                        [m	[32m<option value="MA">Morocco</option>[m
[32m+[m[41m                        [m	[32m<option value="MZ">Mozambique</option>[m
[32m+[m[41m                        [m	[32m<option value="MM">Myanmar</option>[m
[32m+[m[41m                        [m	[32m<option value="NA">Namibia</option>[m
[32m+[m[41m                        [m	[32m<option value="NR">Nauru</option>[m
[32m+[m[41m                        [m	[32m<option value="NP">Nepal</option>[m
[32m+[m[41m                        [m	[32m<option value="NL">Netherlands</option>[m
[32m+[m[41m                        [m	[32m<option value="NC">New Caledonia</option>[m
[32m+[m[41m                        [m	[32m<option value="NZ">New Zealand</option>[m
[32m+[m[41m                        [m	[32m<option value="NI">Nicaragua</option>[m
[32m+[m[41m                        [m	[32m<option value="NE">Niger</option>[m
[32m+[m[41m                        [m	[32m<option value="NG">Nigeria</option>[m
[32m+[m[41m                        [m	[32m<option value="NU">Niue</option>[m
[32m+[m[41m                        [m	[32m<option value="NF">Norfolk Island</option>[m
[32m+[m[41m                        [m	[32m<option value="MP">Northern Mariana Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="NO">Norway</option>[m
[32m+[m[41m                        [m	[32m<option value="OM">Oman</option>[m
[32m+[m[41m                        [m	[32m<option value="PK">Pakistan</option>[m
[32m+[m[41m                        [m	[32m<option value="PW">Palau</option>[m
[32m+[m[41m                        [m	[32m<option value="PS">Palestinian Territory, Occupied</option>[m
[32m+[m[41m                        [m	[32m<option value="PA">Panama</option>[m
[32m+[m[41m                        [m	[32m<option value="PG">Papua New Guinea</option>[m
[32m+[m[41m                        [m	[32m<option value="PY">Paraguay</option>[m
[32m+[m[41m                        [m	[32m<option value="PE">Peru</option>[m
[32m+[m[41m                        [m	[32m<option value="PH">Philippines</option>[m
[32m+[m[41m                        [m	[32m<option value="PN">Pitcairn</option>[m
[32m+[m[41m                        [m	[32m<option value="PL">Poland</option>[m
[32m+[m[41m                        [m	[32m<option value="PT">Portugal</option>[m
[32m+[m[41m                        [m	[32m<option value="PR">Puerto Rico</option>[m
[32m+[m[41m                        [m	[32m<option value="QA">Qatar</option>[m
[32m+[m[41m                        [m	[32m<option value="RE">Réunion</option>[m
[32m+[m[41m                        [m	[32m<option value="RO">Romania</option>[m
[32m+[m[41m                        [m	[32m<option value="RU">Russian Federation</option>[m
[32m+[m[41m                        [m	[32m<option value="RW">Rwanda</option>[m
[32m+[m[41m                        [m	[32m<option value="BL">Saint Barthélemy</option>[m
[32m+[m[41m                        [m	[32m<option value="SH">Saint Helena, Ascension and Tristan da Cunha</option>[m
[32m+[m[41m                        [m	[32m<option value="KN">Saint Kitts and Nevis</option>[m
[32m+[m[41m                        [m	[32m<option value="LC">Saint Lucia</option>[m
[32m+[m[41m                        [m	[32m<option value="MF">Saint Martin (French part)</option>[m
[32m+[m[41m                        [m	[32m<option value="PM">Saint Pierre and Miquelon</option>[m
[32m+[m[41m                        [m	[32m<option value="VC">Saint Vincent and the Grenadines</option>[m
[32m+[m[41m                        [m	[32m<option value="WS">Samoa</option>[m
[32m+[m[41m                        [m	[32m<option value="SM">San Marino</option>[m
[32m+[m[41m                        [m	[32m<option value="ST">Sao Tome and Principe</option>[m
[32m+[m[41m                        [m	[32m<option value="SA">Saudi Arabia</option>[m
[32m+[m[41m                        [m	[32m<option value="SN">Senegal</option>[m
[32m+[m[41m                        [m	[32m<option value="RS">Serbia</option>[m
[32m+[m[41m                        [m	[32m<option value="SC">Seychelles</option>[m
[32m+[m[41m                        [m	[32m<option value="SL">Sierra Leone</option>[m
[32m+[m[41m                        [m	[32m<option value="SG">Singapore</option>[m
[32m+[m[41m                        [m	[32m<option value="SX">Sint Maarten (Dutch part)</option>[m
[32m+[m[41m                        [m	[32m<option value="SK">Slovakia</option>[m
[32m+[m[41m                        [m	[32m<option value="SI">Slovenia</option>[m
[32m+[m[41m                        [m	[32m<option value="SB">Solomon Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="SO">Somalia</option>[m
[32m+[m[41m                        [m	[32m<option value="ZA">South Africa</option>[m
[32m+[m[41m                        [m	[32m<option value="GS">South Georgia and the South Sandwich Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="SS">South Sudan</option>[m
[32m+[m[41m                        [m	[32m<option value="ES">Spain</option>[m
[32m+[m[41m                        [m	[32m<option value="LK">Sri Lanka</option>[m
[32m+[m[41m                        [m	[32m<option value="SD">Sudan</option>[m
[32m+[m[41m                        [m	[32m<option value="SR">Suriname</option>[m
[32m+[m[41m                        [m	[32m<option value="SJ">Svalbard and Jan Mayen</option>[m
[32m+[m[41m                        [m	[32m<option value="SZ">Swaziland</option>[m
[32m+[m[41m                        [m	[32m<option value="SE">Sweden</option>[m
[32m+[m[41m                        [m	[32m<option value="CH">Switzerland</option>[m
[32m+[m[41m                        [m	[32m<option value="SY">Syrian Arab Republic</option>[m
[32m+[m[41m                        [m	[32m<option value="TW">Taiwan, Province of China</option>[m
[32m+[m[41m                        [m	[32m<option value="TJ">Tajikistan</option>[m
[32m+[m[41m                        [m	[32m<option value="TZ">Tanzania, United Republic of</option>[m
[32m+[m[41m                        [m	[32m<option value="TH">Thailand</option>[m
[32m+[m[41m                        [m	[32m<option value="TL">Timor-Leste</option>[m
[32m+[m[41m                        [m	[32m<option value="TG">Togo</option>[m
[32m+[m[41m                        [m	[32m<option value="TK">Tokelau</option>[m
[32m+[m[41m                        [m	[32m<option value="TO">Tonga</option>[m
[32m+[m[41m                        [m	[32m<option value="TT">Trinidad and Tobago</option>[m
[32m+[m[41m                        [m	[32m<option value="TN">Tunisia</option>[m
[32m+[m[41m                        [m	[32m<option value="TR">Turkey</option>[m
[32m+[m[41m                        [m	[32m<option value="TM">Turkmenistan</option>[m
[32m+[m[41m                        [m	[32m<option value="TC">Turks and Caicos Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="TV">Tuvalu</option>[m
[32m+[m[41m                        [m	[32m<option value="UG">Uganda</option>[m
[32m+[m[41m                        [m	[32m<option value="UA">Ukraine</option>[m
[32m+[m[41m                        [m	[32m<option value="AE">United Arab Emirates</option>[m
[32m+[m[41m                        [m	[32m<option value="GB">United Kingdom</option>[m
[32m+[m[41m                        [m	[32m<option value="US">United States</option>[m
[32m+[m[41m                        [m	[32m<option value="UM">United States Minor Outlying Islands</option>[m
[32m+[m[41m                        [m	[32m<option value="UY">Uruguay</option>[m
[32m+[m[41m                        [m	[32m<option value="UZ">Uzbekistan</option>[m
[32m+[m[41m                        [m	[32m<option value="VU">Vanuatu</option>[m
[32m+[m[41m                        [m	[32m<option value="VE">Venezuela, Bolivarian Republic of</option>[m
[32m+[m[41m                        [m	[32m<option value="VN">Viet Nam</option>[m
[32m+[m[41m                        [m	[32m<option value="VG">Virgin Islands, British</option>[m
[32m+[m[41m                        [m	[32m<option value="VI">Virgin Islands, U.S.</option>[m
[32m+[m[41m                        [m	[32m<option value="WF">Wallis and Futuna</option>[m
[32m+[m[41m                        [m	[32m<option value="EH">Western Sahara</option>[m
[32m+[m[41m                        [m	[32m<option value="YE">Yemen</option>[m
[32m+[m[41m                        [m	[32m<option value="ZM">Zambia</option>[m
[32m+[m[41m                        [m	[32m<option value="ZW">Zimbabwe</option>[m
[32m+[m[32m                        </select><br>[m
[32m+[m[32m                        <button class="btn btn-primary" type="submit" onclick="moreinfo()" id="buttonPrint">Print Coupons</button>[m
[32m+[m[32m                    </form>[m
[32m+[m[32m                </div>[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</div>[m
[32m+[m
[32m+[m
[32m+[m[32m <div class="modal fade" id="consentModal" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">[m
[32m+[m[32m    <div class="modal-dialog modal-dialog-centered" role="document">[m
[32m+[m[32m        <div class="modal-content">[m
[32m+[m[32m                <div class="modal-header">[m
[32m+[m[32m                    <h5 class="modal-title" id="exampleModalCenterTitle">Sign Up Now</h5><br>[m
[32m+[m[32m                </div>[m
[32m+[m[32m                <div class="modal-body" id="mfamodalbody">[m
[32m+[m[32m                    <h3>Website usage terms and conditions</h3>[m
[32m+[m[32m                    <p>Welcome to our website. If you continue to browse and use this website, you are agreeing to comply with and be bound by the following terms and conditions of use, which together with our privacy policy govern [business name]&rsquo;s relationship with you in relation to this website. If you disagree with any part of these terms and conditions, please do not use our website.</p>[m
[32m+[m[32m                    <p>The term &lsquo;[business name]&rsquo; or &lsquo;us&rsquo; or &lsquo;we&rsquo; refers to the owner of the website whose registered office is [address]. Our company registration number is [company registration number and place of registration]. The term &lsquo;you&rsquo; refers to the user or viewer of our website.</p>[m
[32m+[m[32m                    <p>The use of this website is subject to the following terms of use:</p>[m
[32m+[m[32m                    <ul>[m
[32m+[m[32m                    <li>The content of the pages of this website is for your general information and use only. It is subject to change without notice.</li>[m
[32m+[m[32m                    <li>This website uses cookies to monitor browsing preferences. If you do allow cookies to be used, the following personal information may be stored by us for use by third parties: [insert list of information].</li>[m
[32m+[m[32m                    <li>Neither we nor any third parties provide any warranty or guarantee as to the accuracy, timeliness, performance, completeness or suitability of the information and materials found or offered on this website for any particular purpose. You acknowledge that such information and materials may contain inaccuracies or errors and we expressly exclude liability for any such inaccuracies or errors to the fullest extent permitted by law.</li>[m
[32m+[m[32m                    <li>Your use of any information or materials on this website is entirely at your own risk, for which we shall not be liable. It shall be your own responsibility to ensure that any products, services or information available through this website meet your specific requirements.</li>[m
[32m+[m[32m                    <li>This website contains material which is owned by or licensed to us. This material includes, but is not limited to, the design, layout, look, appearance and graphics. Reproduction is prohibited other than in accordance with the copyright notice, which forms part of these terms and conditions.</li>[m
[32m+[m[32m                    <li>All trademarks reproduced in this website, which are not the property of, or licensed to the operator, are acknowledged on the website.</li>[m
[32m+[m[32m                    <li>Unauthorised use of this website may give rise to a claim for damages and/or be a criminal offence.</li>[m
[32m+[m[32m                    <li>From time to time, this website may also include links to other websites. These links are provided for your convenience to provide further information. They do not signify that we endorse the website(s). We have no responsibility for the content of the linked website(s).</li>[m
[32m+[m[32m                    <li>Your use of this website and any dispute arising out of such use of the website is subject to the laws of England, Northern Ireland, Scotland and Wales.</li>[m
[32m+[m[32m                    </ul>[m
[32m+[m[32m                </div>[m
[32m+[m[32m                <div class="modal-footer">[m
[32m+[m[32m                    <div  style="float: left;"><input type="checkbox" id="acceptterms" name="acceptterms" onclick="acceptterms()" value="Accept Terms"> &nbsp;&nbsp;I hereby consent and[m
[32m+[m[32m                        acknowledge my agreement to the terms set forth in the Terms and Conditions and any[m
[32m+[m[32m                        subsequent changes in office policy. I understand that this consent shall remain in force[m
[32m+[m[32m                        from this time forward.[m
[32m+[m[32m                    </div>&nbsp;&nbsp;&nbsp;[m
[32m+[m[32m                    <button class="btn btn-primary" type="button" id="confirm"  onclick="acceptcompleted()" disabled>Confirm</button>[m
[32m+[m[32m                    <button class="btn btn-primary" type="button" onclick="closepopup()">Cancel</button>[m
[32m+[m[32m                </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</div>[m
[32m+[m[32m<style>[m
[32m+[m[32m    .modal-dialog {[m
[32m+[m[32m        max-width: 800;[m
[32m+[m[32m    }[m
[32m+[m[32m</style>[m
[32m+[m
[32m+[m[32m<script type="text/javascript">[m
[32m+[m[32m    function moreinfo() {[m
[32m+[m[32m        console.log("moreinfo()");[m
[32m+[m[32m        $("#moreinfo").modal("show");[m
[32m+[m[32m    }[m
[32m+[m[32m    window.addEventListener('load', function () {[m
[32m+[m[32m        testconsent = '{{consent}}';[m
[32m+[m[32m        console.log("check_consent()");[m
[32m+[m[32m        console.log(testconsent);[m
[32m+[m[32m        if (testconsent.trim() == '')[m
[32m+[m[32m        {[m
[32m+[m[32m            $("#consentModal").modal("show");[m
[32m+[m[32m        }[m
[32m+[m[32m    })[m
[32m+[m
[32m+[m[32m    function acceptcompleted() {[m
[32m+[m[32m        console.log("acceptcompleted()");[m
[32m+[m[32m        window.location = "/consumerproducts/acceptterms";[m
[32m+[m[32m        $("#consentModal").modal("hide");[m
[32m+[m[32m    }[m
[32m+[m
[32m+[m[32m    function closepopup() {[m
[32m+[m[32m        console.log("closepopup()");[m
[32m+[m[32m        $("#consentModal").modal("hide");[m
[32m+[m[32m    }[m
[32m+[m
[32m+[m[32m    function acceptterms() {[m
[32m+[m[32m        console.log("acceptterms()");[m
[32m+[m[32m        if($("#acceptterms").prop("checked") == true)[m
[32m+[m[32m        {[m
[32m+[m[32m            $("#confirm").prop('disabled', false);[m
[32m+[m[32m        }[m
[32m+[m[32m        else[m
[32m+[m[32m        {[m
[32m+[m[32m            $("#confirm").prop('disabled', true);[m
[32m+[m[32m        }[m
[32m+[m[32m    }[m
[32m+[m[32m</script>[m
[32m+[m
[32m+[m
[32m+[m[32m{% endblock %}[m
[32m+[m
[32m+[m[32m{% block footer %}[m
[32m+[m[32m{% endblock %}[m
\ No newline at end of file[m
[1mdiff --git a/_consumerproducts/templates/consumerproducts/index.html b/_consumerproducts/templates/consumerproducts/index.html[m
[1mnew file mode 100644[m
[1mindex 0000000..10589cb[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/templates/consumerproducts/index.html[m
[36m@@ -0,0 +1,89 @@[m
[32m+[m[32m{% extends "consumerproducts/template.html" %}[m
[32m+[m
[32m+[m[32m{% block content %}[m
[32m+[m[32m<header class="page-header page-header-dark bg-img-cover"[m
[32m+[m[32m    style='color: {{config.settings.app_primary_color}} !important; background-color: {{config.settings.app_primary_color}} !important;'>[m
[32m+[m[32m    <div class="page-header-content py-5">[m
[32m+[m[32m        <div class="container">[m
[32m+[m[32m            <div class="row justify-content-left">[m
[32m+[m[32m                <div class="col-xl-6 text-left">[m
[32m+[m[32m                    <div data-aos="fade-up">[m
[32m+[m[32m                        <h1 class="page-header-title">{{ config.settings.app_slogan }}</h1>[m
[32m+[m[32m                        <p class="page-header-text">{{ config.settings.app_subslogan }} </p>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                    <button class="btn btn-marketing rounded-pill btn-secondary" data-aos="fade-up" data-aos-delay="100" style="color: {{config.settings.app_primary_color}} !important;">[m
[32m+[m[32m                        Learn More[m
[32m+[m[32m                    </button>[m
[32m+[m[32m                </div>[m
[32m+[m[32m                <div class="col-xl-4 col-lg-10 text-right">[m
[32m+[m[32m                    <img src="{{ config.settings.app_banner_img_1 }}">[m
[32m+[m[32m                </div>[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m    <div class="svg-border-rounded text-white">[m
[32m+[m[32m        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144.54 17.34" preserveAspectRatio="none"[m
[32m+[m[32m             fill="currentColor">[m
[32m+[m[32m            <path d="M144.54,17.34H0V0H144.54ZM0,0S32.36,17.34,72.27,17.34,144.54,0,144.54,0"></path>[m
[32m+[m[32m        </svg>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</header>[m
[32m+[m[32m<section class="bg-white py-10">[m
[32m+[m[32m    <div class="container">[m
[32m+[m[32m        <div class="row text-center">[m
[32m+[m[32m            <div class="col-lg-4 mb-5 mb-lg-0">[m
[32m+[m[32m                <div class="icon-stack icon-stack-xl bg-primary text-white mb-4"><i data-feather="dollar-sign"></i></div>[m
[32m+[m[32m                <h2>Get your Discounts</h2>[m
[32m+[m[32m                <p class="mb-0">Stock up with discounts our amazing products.</p>[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div class="col-lg-4 mb-5 mb-lg-0">[m
[32m+[m[32m                <div class="icon-stack icon-stack-xl bg-primary text-white mb-4"><i data-feather="heart"></i></div>[m
[32m+[m[32m                <h2>Our Products</h2>[m
[32m+[m[32m                <p class="mb-0">Building products that matter.</p>[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div class="col-lg-4">[m
[32m+[m[32m                <div class="icon-stack icon-stack-xl bg-primary text-white mb-4"><i data-feather="map-pin"></i></div>[m
[32m+[m[32m                <h2>Available Near You</h2>[m
[32m+[m[32m                <p class="mb-0">Find our products near you.</p>[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m    <div class="svg-border-rounded text-light">[m
[32m+[m[32m        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 144.54 17.34" preserveAspectRatio="none"[m
[32m+[m[32m             fill="currentColor">[m
[32m+[m[32m            <path d="M144.54,17.34H0V0H144.54ZM0,0S32.36,17.34,72.27,17.34,144.54,0,144.54,0"></path>[m
[32m+[m[32m        </svg>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</section>[m
[32m+[m[32m<section class="bg-light py-10" >[m
[32m+[m[32m    <div class="container">[m
[32m+[m[32m        <div class="row justify-content-center">[m
[32m+[m[32m            <div class="col-xl-6 col-lg-8 col-md-10 text-center">[m
[32m+[m[32m                <h2>Have any questions?</h2>[m
[32m+[m[32m                <p class="lead text-gray-500 mb-5">We'd love to hear from you. Contact us to get more information or chat with us now.</p>[m
[32m+[m[32m                <a class="btn btn-primary btn-marketing rounded-pill" href="#!">Contact us</a>[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</section>[m
[32m+[m[32m<section class="bg-white py-10">[m
[32m+[m[32m    <div class="container">[m
[32m+[m[32m        <div class="row justify-content-center">[m
[32m+[m[32m            <div class="col-xl-5 col-lg-8 col-md-10 text-left">[m
[32m+[m[32m                <h4>Get the latest discounts</h4>[m
[32m+[m[32m                <p class="lead text-gray-500 mb-0">Stay in the loop with the latest product news and discounts!</p>[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div class="col-xl-5 col-lg-8 col-md-10 text-right">[m
[32m+[m[32m                <div class="input-group mb-2">[m
[32m+[m[32m                    <input class="form-control form-control-solid" type="text" placeholder="youremail@example.com" aria-label="Recipient's username" aria-describedby="button-addon2" />[m
[32m+[m[32m                    <div class="input-group-append"><button class="btn btn-primary" id="button-addon2" type="button">Sign up</button></div>[m
[32m+[m[32m                </div>[m
[32m+[m[32m                <div class="small text-gray-500">You can unsubscribe at any time.</div>[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</section>[m
[32m+[m[32m{% endblock %}[m
[32m+[m
[32m+[m[32m{% block footer %}[m
[32m+[m[32m{% endblock %}[m
\ No newline at end of file[m
[1mdiff --git a/_consumerproducts/templates/consumerproducts/login.html b/_consumerproducts/templates/consumerproducts/login.html[m
[1mnew file mode 100644[m
[1mindex 0000000..4e0cd91[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/templates/consumerproducts/login.html[m
[36m@@ -0,0 +1,9 @@[m
[32m+[m[32m{% extends "consumerproducts/template.html" %}[m
[32m+[m
[32m+[m[32m{% block content %}[m
[32m+[m[32m    <br /><br />[m
[32m+[m[32m    {% include '/components/template-login-widget.html' %}[m
[32m+[m[32m{% endblock %}[m
[32m+[m
[32m+[m[32m{% block footer %}[m
[32m+[m[32m{% endblock %}[m
\ No newline at end of file[m
[1mdiff --git a/_consumerproducts/templates/consumerproducts/navitems.html b/_consumerproducts/templates/consumerproducts/navitems.html[m
[1mnew file mode 100644[m
[1mindex 0000000..9d2b28f[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/templates/consumerproducts/navitems.html[m
[36m@@ -0,0 +1,11 @@[m
[32m+[m[32m        <div class="collapse navbar-collapse" id="navbarSupportedContent">[m
[32m+[m[32m            <ul class="navbar-nav ml-auto mr-lg-5">[m
[32m+[m[32m                <li class="nav-item"><a class="nav-link" href="../index">Home</a></li>[m
[32m+[m[32m                <li class="nav-item no-caret">[m
[32m+[m[32m                    <a class="nav-link" id="navbarDropdownPages" href="#" role="button"  aria-haspopup="true" >Our Products</a>[m
[32m+[m[32m                </li>[m
[32m+[m[32m                <li class="nav-item no-caret">[m
[32m+[m[32m                    <a class="nav-link" id="navbarDropdownPages" href="/login" role="button" aria-haspopup="true" >Get Discounts</a>[m
[32m+[m[32m                </li>[m
[32m+[m[32m            </ul>[m
[32m+[m[32m        </div>[m
\ No newline at end of file[m
[1mdiff --git a/_consumerproducts/templates/consumerproducts/navitemslogin.html b/_consumerproducts/templates/consumerproducts/navitemslogin.html[m
[1mnew file mode 100644[m
[1mindex 0000000..cf93dab[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/templates/consumerproducts/navitemslogin.html[m
[36m@@ -0,0 +1,52 @@[m
[32m+[m[32m        <div class="collapse navbar-collapse" id="navbarSupportedContent">[m
[32m+[m[32m            <ul class="navbar-nav ml-auto mr-lg-5">[m
[32m+[m[32m                <li class="nav-item"><a class="nav-link" href="../index">Home</a></li>[m
[32m+[m[32m                <li class="nav-item"><a class="nav-link" href="/consumerproducts/discounts">Discounts</a></li>[m
[32m+[m[32m                <li class="nav-item dropdown dropdown-xl no-caret">[m
[32m+[m[32m                    <a class="nav-link dropdown-toggle" id="navbarDropdownDemos" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Your Account<i class="fas fa-chevron-right dropdown-arrow"></i></a>[m
[32m+[m[32m                    <div class="dropdown-menu dropdown-menu-right animated--fade-in-up mr-lg-n15" aria-labelledby="navbarDropdownDemos">[m
[32m+[m[32m                        <div class="row no-gutters">[m
[32m+[m[32m                            <div class="col-lg-5 p-lg-3 bg-img-cover overlay overlay-primary overlay-70 d-none d-lg-block">[m
[32m+[m[32m                                <div class="d-flex h-100 w-100 align-items-center justify-content-center">[m
[32m+[m[32m                                    <div class="text-white text-center z-1">[m
[32m+[m[32m                                        <div class="mb-3">We are here for you.</div>[m
[32m+[m[32m                                    </div>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                            <div class="col-lg-7 p-lg-5">[m
[32m+[m[32m                                <div class="row">[m
[32m+[m[32m                                    <div class="col-lg-6">[m
[32m+[m[32m                                        <h6 class="dropdown-header text-primary">Account</h6>[m
[32m+[m[32m                                        <a class="dropdown-item" href="/consumerproducts/profile">Your Profile</a>[m
[32m+[m[32m                                        <a class="dropdown-item" href="/userapps">More Products</a>[m
[32m+[m[32m                                        <a class="dropdown-item" href="/profile">Your Tokens</a>[m
[32m+[m[32m                                    </div>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                </li>[m
[32m+[m[32m                <li class="nav-item dropdown dropdown-xl no-caret">[m
[32m+[m[32m                    <a class="nav-link dropdown-toggle" id="navbarDropdownDemos" href="#" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Family Access<i class="fas fa-chevron-right dropdown-arrow"></i></a>[m
[32m+[m[32m                    <div class="dropdown-menu dropdown-menu-right animated--fade-in-up mr-lg-n15" aria-labelledby="navbarDropdownDemos">[m
[32m+[m[32m                        <div class="row no-gutters">[m
[32m+[m[32m                            <div class="col-lg-5 p-lg-3 bg-img-cover overlay overlay-primary overlay-70 d-none d-lg-block">[m
[32m+[m[32m                                <div class="d-flex h-100 w-100 align-items-center justify-content-center">[m
[32m+[m[32m                                    <div class="text-white text-center z-1">[m
[32m+[m[32m                                        <div class="mb-3">We are here for you.</div>[m
[32m+[m[32m                                    </div>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                            <div class="col-lg-7 p-lg-5">[m
[32m+[m[32m                                <div class="row">[m
[32m+[m[32m                                    <div class="col-lg-6">[m
[32m+[m[32m                                        <h6 class="dropdown-header text-primary">Family</h6>[m
[32m+[m[32m                                        <a class="dropdown-item" href="/manageusers">Manage Family</a>[m
[32m+[m[32m                                    </div>[m
[32m+[m[32m                                </div>[m
[32m+[m[32m                            </div>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                </li>[m
[32m+[m[32m            </ul>[m
[32m+[m[32m        </div>[m
\ No newline at end of file[m
[1mdiff --git a/_consumerproducts/templates/consumerproducts/profile.html b/_consumerproducts/templates/consumerproducts/profile.html[m
[1mnew file mode 100644[m
[1mindex 0000000..4ecca17[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/templates/consumerproducts/profile.html[m
[36m@@ -0,0 +1,126 @@[m
[32m+[m[32m{% extends "consumerproducts/template.html" %}[m
[32m+[m
[32m+[m[32m{% block content %}[m
[32m+[m[32m <section class="bg-light py-5">[m
[32m+[m[32m    <div class="container">[m
[32m+[m[32m        <div class="row">[m
[32m+[m[32m            <div class="col-md-6">[m
[32m+[m[32m                <div class="card border-bottom">[m
[32m+[m[32m                    <div class="card-header">Account</div>[m
[32m+[m[32m                    <div class="card-body">[m
[32m+[m[32m                          <form class="form-horizontal" action='updateuserinfo' method="POST">[m
[32m+[m[32m                              <div class="form-group input-group">[m
[32m+[m[41m                             [m	[32m  <div class="input-group-prepend">[m
[32m+[m[41m                            [m		[32m  <span class="input-group-text"> <i class="fa fa-user"></i> </span>[m
[32m+[m[41m                            [m		[32m</div>[m
[32m+[m[41m                            [m	[32m  <input name="firstname" class="form-control" id="firstname" placeholder="First Name" type="text" value="{{ user_info2['profile']['firstName'] }}">[m
[32m+[m[32m                              </div>[m
[32m+[m
[32m+[m[32m                              <div class="form-group input-group">[m
[32m+[m[32m                                <div class="input-group-prepend">[m
[32m+[m[41m                          [m		[32m    <span class="input-group-text"> <i class="fa fa-user"></i> </span>[m
[32m+[m[41m                          [m		[32m  </div>[m
[32m+[m[32m                                <input name="lastname" class="form-control" id="lastname" placeholder="Last Name" type="text" value="{{ user_info2['profile']['lastName']  }}">[m
[32m+[m[32m                              </div>[m
[32m+[m
[32m+[m[32m                              <div class="form-group input-group">[m
[32m+[m[41m                              [m	[32m<div class="input-group-prepend">[m
[32m+[m[41m                          [m		[32m    <span class="input-group-text"> <i class="fa fa-envelope"></i> </span>[m
[32m+[m[41m                          [m		[32m  </div>[m
[32m+[m[32m                                <input name="email" class="form-control" id="email" placeholder="Email address" type="email" value="{{ user_info2['profile']['email']  }}">[m
[32m+[m[32m                              </div>[m
[32m+[m
[32m+[m[32m                              <div class="form-group input-group">[m
[32m+[m[41m                              [m	[32m<div class="input-group-prepend">[m
[32m+[m[41m                          [m		[32m    <span class="input-group-text"> <i class="fa fa-phone"></i> </span>[m
[32m+[m[41m                          [m		[32m  </div>[m
[32m+[m[41m                          [m			[32m<input name="mobilePhone" id="mobilePhone" class="form-control" placeholder="Mobile Phone" type="text" value="{{ user_info2['profile']['mobilePhone']  }}">[m
[32m+[m[32m                              </div>[m
[32m+[m[32m                              <div class="form-group input-group">[m
[32m+[m[32m                                    <div class="input-group-prepend">[m
[32m+[m[41m                          [m		[32m        <span class="input-group-text"> <i class="fa fa-check"></i> </span>[m
[32m+[m[32m                                    </div>[m
[32m+[m[41m                          [m			[32m<input name="consent" id="consent" class="form-control" type="text" value="{{ consent }}" disabled>&nbsp;&nbsp;[m
[32m+[m[41m                          [m			[32m<button type="button" onclick="resetconsent()" class="btn btn-primary">Reset Consent</button>[m
[32m+[m[32m                              </div>[m
[32m+[m[32m                              <input name="nconsent" id="nconsent" class="form-control" type="hidden" value="{{ consent }}">[m
[32m+[m[32m                              <input id="user_id" name="user_id" class="form-control" type="hidden" value="{{ user_info2['id'] }}">[m
[32m+[m[32m                              <div class="form-group">[m
[32m+[m[32m                              <button type="submit" class="btn btn-primary btn-block">Update Account</button>[m
[32m+[m[32m                              </div>[m
[32m+[m[32m                          </form>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                </div>[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div class="col-md-6">[m
[32m+[m[32m                <div class="card border-bottom">[m
[32m+[m[32m                    <div class="card-header">Subscriptions</div>[m
[32m+[m[32m                    <div class="card-body" >[m
[32m+[m[32m                        <div class="custom-control custom-checkbox">[m
[32m+[m[32m                            <input class="custom-control-input" id="huggies" type="checkbox" onclick="updatecomm('huggies')" {{ 'checked' if user_info2['profile']['local_app_huggies_comm']|string() == 'true' else '' }}>[m
[32m+[m[32m                            <label class="custom-control-label" for="huggies" style="background: none;">Huggies Communications</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="custom-control custom-checkbox">[m
[32m+[m[32m                            <input class="custom-control-input" id="pullups" type="checkbox" onclick="updatecomm('pullups')" {{ 'checked' if user_info2['profile']['local_app_pullups_comm']|string() ==  'true' else '' }}>[m
[32m+[m[32m                            <label class="custom-control-label" for="pullups" style="background: none;">Pull-Ups® Communications</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="custom-control custom-checkbox">[m
[32m+[m[32m                            <input class="custom-control-input" id="goodnights" type="checkbox" onclick="updatecomm('goodnights')" {{ 'checked' if user_info2['profile']['local_app_goodnights_comm']|string() == 'true' else '' }}>[m
[32m+[m[32m                            <label class="custom-control-label" for="goodnights" style="background: none;">GoodNites® Communications</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="custom-control custom-checkbox">[m
[32m+[m[32m                            <input class="custom-control-input" id="ubykotex" type="checkbox" onclick="updatecomm('ubykotex')" {{ 'checked' if user_info2['profile']['local_app_ubykotex_comm']|string() == 'true' else '' }}>[m
[32m+[m[32m                            <label class="custom-control-label" for="ubykotex" style="background: none;">UByKotex® Communications</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="custom-control custom-checkbox">[m
[32m+[m[32m                            <input class="custom-control-input" id="depend" type="checkbox" onclick="updatecomm('depend')" {{ 'checked' if user_info2['profile']['local_app_depend_comm']|string() == 'true' else '' }}>[m
[32m+[m[32m                            <label class="custom-control-label" for="depend" style="background: none;">Depend® Communications</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="custom-control custom-checkbox">[m
[32m+[m[32m                            <input class="custom-control-input" id="poise" type="checkbox" onclick="updatecomm('poise')" {{ 'checked' if user_info2['profile']['local_app_poise_comm']|string() == 'true' else '' }}>[m
[32m+[m[32m                            <label class="custom-control-label" for="poise" style="background: none;">Poise® Communications</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                        <div class="custom-control custom-checkbox">[m
[32m+[m[32m                            <input class="custom-control-input" id="kcc" type="checkbox" onclick="updatecomm('kcc')" {{ 'checked' if user_info2['profile']['local_app_kcc_comm']|string() == 'true' else '' }}>[m
[32m+[m[32m                            <label class="custom-control-label" for="kcc" style="background: none;">Yes! I want to be the first to know about exciting offers, product updates and more from Scott® and other Kimberly-Clark brands, including Cottonelle®, Kleenex® and VIVA®.</label>[m
[32m+[m[32m                        </div>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                </div>[m
[32m+[m[32m                <br>[m
[32m+[m[32m                {% include '//components/template-mfaenrollment.html' %}[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m    </div>[m
[32m+[m[32m</section>[m
[32m+[m[32m    <script type="text/javascript">[m
[32m+[m
[32m+[m[32m        function updatecomm(comm){[m
[32m+[m[32m            console.log("updatecomm()");[m
[32m+[m[32m            console.log($("#"+comm).is(":checked"));[m
[32m+[m[32m            var $label = $("label[for='"+comm+"']")[m
[32m+[m[32m            ischecked = $("#"+comm).is(":checked")[m
[32m+[m[32m            if (ischecked) {[m
[32m+[m[32m                window.location = "/consumerproducts/updatecomm/" + comm+"?set=true&user_id={{user_info2['id']}}&product=" + $label.text();[m
[32m+[m[32m            }[m
[32m+[m[32m            else{[m
[32m+[m[32m                window.location = "/consumerproducts/updatecomm/" + comm+"?set=false&user_id={{user_info2['id']}}&product=" + $label.text();[m
[32m+[m[32m            }[m
[32m+[m[32m        }[m
[32m+[m
[32m+[m[32m        function resetconsent() {[m
[32m+[m[32m            console.log("resetconsent()");[m
[32m+[m[32m            $("#consent").val("");[m
[32m+[m[32m            window.location = "/consumerproducts/clearconsent/{{user_info2['id']}}" ;[m
[32m+[m[32m        }[m
[32m+[m[32m    </script>[m
[32m+[m
[32m+[m[32m    <style>[m
[32m+[m[32m        .modal-dialog {[m
[32m+[m[32m            max-width: 800;[m
[32m+[m[32m        }[m
[32m+[m[32m    </style>[m
[32m+[m
[32m+[m[32m{% endblock %}[m
[32m+[m
[32m+[m[32m{% block footer %}[m
[32m+[m[32m{% endblock %}[m
\ No newline at end of file[m
[1mdiff --git a/_consumerproducts/templates/consumerproducts/template.html b/_consumerproducts/templates/consumerproducts/template.html[m
[1mnew file mode 100644[m
[1mindex 0000000..ef8dd90[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/templates/consumerproducts/template.html[m
[36m@@ -0,0 +1,70 @@[m
[32m+[m[32m<!--Do Not Remove any parts of this document unless you expect to not use out of the box behaviours-->[m
[32m+[m[32m<html lang="en">[m
[32m+[m[32m    {% include '//components/template-header-meta.html' %}[m
[32m+[m[32m    <body>[m
[32m+[m[32m        <div class="bg-light" >[m
[32m+[m[32m            <div class="container py-1 bg-light" >[m
[32m+[m[32m                <div class="row">[m
[32m+[m[32m                    <div class="col-lg-6 mb-3 mb-lg-0 text-left txt-primary text-xs" style="justify: middle;">[m
[32m+[m[32m                     Part of the Kimberly-Clark Family: <div id="logos" style="display: inline-block;"></div>[m
[32m+[m[32m                    </div>[m
[32m+[m[32m                </div>[m
[32m+[m[32m            </div>[m
[32m+[m[32m        </div>[m
[32m+[m[32m        <script>[m
[32m+[m[32m            var apps;[m
[32m+[m[32m            $.ajax({[m
[32m+[m[32m                url:'/consumerproducts/apps',[m
[32m+[m[32m                type: "GET",[m
[32m+[m[32m                data:{[m[41m                [m
[32m+[m[32m                },[m[41m    [m
[32m+[m[32m                complete: function (response) {[m
[32m+[m[32m                    console.log(response.responseText);[m
[32m+[m[32m                     apps = JSON.parse(response.responseText);[m
[32m+[m[32m                    console.log(apps);[m
[32m+[m[32m                    var applinks = "" ;[m
[32m+[m[32m                    for (i = 0; i < apps.length; i++) {[m
[32m+[m[32m                        url = apps[i]._links.appLinks[0].href;[m
[32m+[m[32m                        image = apps[i]._links.logo[0].href;[m
[32m+[m[32m                        applinks = applinks + "<a href="+url +"><img border=0 style='height:25px;' src=" + image +"></a>";[m
[32m+[m[32m                    }[m
[32m+[m[41m                    [m
[32m+[m[32m                    $("#logos").html(applinks);[m
[32m+[m[32m                },[m
[32m+[m[32m                error: function () {[m
[32m+[m[32m                    alert('Bummer: there was an error!');[m
[32m+[m[32m                },[m
[32m+[m[32m            });[m
[32m+[m[41m            [m
[32m+[m[41m            [m
[32m+[m[32m        </script>[m
[32m+[m[32m        <div id="layoutDefault">[m
[32m+[m[32m            <div id="layoutDefault_content">[m
[32m+[m[32m                <main>[m
[32m+[m[32m                    {% if "login" in request.path %}[m
[32m+[m[32m                        {% set navitems ="navitems.html" %}[m
[32m+[m[32m                    {% elif "index" in request.path %}[m
[32m+[m[32m                        {% set navitems ="navitems.html" %}[m
[32m+[m[32m                    {% elif "registration" in request.path %}[m
[32m+[m[32m                        {% set navitems ="navitems.html" %}[m
[32m+[m[32m                    {% elif "/" == request.path %}[m
[32m+[m[32m                        {% set navitems ="navitems.html" %}[m
[32m+[m[32m                    {% else %}[m
[32m+[m[32m                        {% set navitems ="navitemslogin.html" %}[m
[32m+[m[32m                    {% endif %}[m
[32m+[m[32m                    {% with mynavitems=navitems %}[m
[32m+[m[32m                        {% include '//components/template-navigation.html' %}[m
[32m+[m[32m                    {% endwith %}[m
[32m+[m[32m                    {% block content %}{% endblock %}[m
[32m+[m[32m                </main>[m
[32m+[m[32m            </div>[m
[32m+[m[32m            <div id="layoutDefault_footer">[m
[32m+[m[32m                {% block footer %}{% endblock %}[m
[32m+[m[32m            </div>[m
[32m+[m[32m            {% with color="black" %}[m
[32m+[m[32m                {% include '//components/template-footer.html' %}[m
[32m+[m[32m            {% endwith %}[m
[32m+[m[32m        </div>[m
[32m+[m[32m        {% include '//components/template-footer-scripts.html' %}[m
[32m+[m[32m    </body>[m
[32m+[m[32m</html>[m
[1mdiff --git a/_consumerproducts/views.py b/_consumerproducts/views.py[m
[1mnew file mode 100644[m
[1mindex 0000000..3837b26[m
[1m--- /dev/null[m
[1m+++ b/_consumerproducts/views.py[m
[36m@@ -0,0 +1,253 @@[m
[32m+[m[32mimport logging[m
[32m+[m[32mimport datetime[m
[32m+[m[32mimport json[m
[32m+[m
[32m+[m[32mfrom flask import render_template, session, request, redirect, url_for[m
[32m+[m[32mfrom flask import Blueprint[m
[32m+[m[32mfrom utils.udp import SESSION_INSTANCE_SETTINGS_KEY, get_udp_ns_fieldname[m
[32m+[m[32mfrom utils.okta import TokenUtil, OktaAdmin[m
[32m+[m[32mfrom GlobalBehaviorandComponents.mfaenrollment import get_enrolled_factors[m
[32m+[m
[32m+[m[32mfrom GlobalBehaviorandComponents.validation import is_authenticated, get_userinfo[m
[32m+[m
[32m+[m[32mlogger = logging.getLogger(__name__)[m
[32m+[m
[32m+[m[32m# set blueprint[m
[32m+[m[32mconsumerproducts_views_bp = Blueprint('consumerproducts_views_bp', __name__, template_folder='templates', static_folder='static', static_url_path='static')[m
[32m+[m
[32m+[m
[32m+[m[32m# Required for Login Landing Page[m
[32m+[m[32m@consumerproducts_views_bp.route("/profile")[m
[32m+[m[32m@is_authenticated[m
[32m+[m[32mdef consumerproducts_profile():[m
[32m+[m[32m    user_info = get_userinfo()[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m[32m    user = okta_admin.get_user(user_info["sub"])[m
[32m+[m[32m    userapp = okta_admin.get_user_application_by_current_client_id(user_info["sub"])[m
[32m+[m
[32m+[m[32m    if get_udp_ns_fieldname("consent") in userapp["profile"]:[m
[32m+[m[32m        logging.debug(user)[m
[32m+[m[32m        consent = userapp["profile"][get_udp_ns_fieldname("consent")][m
[32m+[m[32m        logging.debug(consent)[m
[32m+[m[32m        if consent.strip() == "":[m
[32m+[m[32m            consent = ''[m
[32m+[m[32m    else:[m
[32m+[m[32m        consent = ''[m
[32m+[m[32m    logging.debug(consent)[m
[32m+[m
[32m+[m[32m    factors = get_enrolled_factors(user["id"])[m
[32m+[m
[32m+[m[32m    return render_template([m
[32m+[m[32m        "consumerproducts/profile.html",[m
[32m+[m[32m        id_token=TokenUtil.get_id_token(request.cookies),[m
[32m+[m[32m        access_token=TokenUtil.get_access_token(request.cookies),[m
[32m+[m[32m        user_info=get_userinfo(),[m
[32m+[m[32m        user_info2=user,[m
[32m+[m[32m        config=session[SESSION_INSTANCE_SETTINGS_KEY],[m
[32m+[m[32m        factors=factors,[m
[32m+[m[32m        consent=consent)[m
[32m+[m
[32m+[m
[32m+[m[32m# Required for Login Landing Page[m
[32m+[m[32m@consumerproducts_views_bp.route("/discounts")[m
[32m+[m[32m@is_authenticated[m
[32m+[m[32mdef consumerproducts_discounts():[m
[32m+[m[32m    user_info = get_userinfo()[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m[32m    user = okta_admin.get_user_application_by_current_client_id(user_info["sub"])[m
[32m+[m[32m    logging.debug(user)[m
[32m+[m[32m    if get_udp_ns_fieldname("consent") in user["profile"]:[m
[32m+[m[32m        logging.debug(user)[m
[32m+[m[32m        consent = user["profile"][get_udp_ns_fieldname("consent")][m
[32m+[m[32m        logging.debug(consent)[m
[32m+[m[32m        if consent.strip() == "":[m
[32m+[m[32m            consent = ''[m
[32m+[m[32m    else:[m
[32m+[m[32m        consent = ''[m
[32m+[m[32m    logging.debug(consent)[m
[32m+[m
[32m+[m[32m    return render_template([m
[32m+[m[32m        "consumerproducts/discounts.html",[m
[32m+[m[32m        id_token=TokenUtil.get_id_token(request.cookies),[m
[32m+[m[32m        access_token=TokenUtil.get_access_token(request.cookies),[m
[32m+[m[32m        user_info=get_userinfo(),[m
[32m+[m[32m        user_info2=user,[m
[32m+[m[32m        consent=consent,[m
[32m+[m[32m        config=session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m
[32m+[m
[32m+[m[32m@consumerproducts_views_bp.route("/acceptterms")[m
[32m+[m[32m@is_authenticated[m
[32m+[m[32mdef consumerproducts_accept_terms():[m
[32m+[m[32m    logger.debug("consumerproducts_accept_terms()")[m
[32m+[m[32m    user_info = get_userinfo()[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m[32m    user = okta_admin.get_user(user_info["sub"])[m
[32m+[m[32m    user_id = user["id"][m
[32m+[m
[32m+[m[32m    now = datetime.datetime.now()[m
[32m+[m[32m    # dd/mm/YY H:M:S[m
[32m+[m[32m    consent = now.strftime("%d/%m/%Y %H:%M:%S")[m
[32m+[m
[32m+[m[32m    user_data = {"profile": {get_udp_ns_fieldname("consent"): consent}}[m
[32m+[m[32m    user_update_response = okta_admin.update_application_user_profile(user_id, user_data)[m
[32m+[m
[32m+[m[32m    if user_update_response:[m
[32m+[m[32m        message = "Thank you for completing the Consent Form."[m
[32m+[m[32m    else:[m
[32m+[m[32m        message = "Error During consent"[m
[32m+[m
[32m+[m[32m    return redirect([m
[32m+[m[32m        url_for([m
[32m+[m[32m            "consumerproducts_views_bp.consumerproducts_discounts",[m
[32m+[m[32m            _external="True",[m
[32m+[m[32m            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],[m
[32m+[m[32m            user_id=user_id,[m
[32m+[m[32m            message=message))[m
[32m+[m
[32m+[m
[32m+[m[32mdef safe_get_dict(mydict, key):[m
[32m+[m[32m    myval = ""[m
[32m+[m[32m    mydictval = mydict.get(key)[m
[32m+[m[32m    if mydictval:[m
[32m+[m[32m        if mydictval.strip() != "":[m
[32m+[m[32m            myval = mydictval.strip()[m
[32m+[m[32m    return myval[m
[32m+[m
[32m+[m
[32m+[m[32m@consumerproducts_views_bp.route("/updateprofile", methods=["POST"])[m
[32m+[m[32m@is_authenticated[m
[32m+[m[32mdef consumerproducts_add_schedule():[m
[32m+[m[32m    logger.debug("consumerproducts_updateprofile")[m
[32m+[m[32m    user_info = get_userinfo()[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m
[32m+[m[32m    country = safe_get_dict(request.form, 'country')[m
[32m+[m[32m    dob = safe_get_dict(request.form, 'dob')[m
[32m+[m[32m    gender = safe_get_dict(request.form, 'gender')[m
[32m+[m
[32m+[m[32m    user_data = {"profile": {[m
[32m+[m[32m        "countryCode": country,[m
[32m+[m[32m        get_udp_ns_fieldname("dob"): dob,[m
[32m+[m[32m        get_udp_ns_fieldname("gender"): gender,[m
[32m+[m[32m    }}[m
[32m+[m
[32m+[m[32m    user_update_response = okta_admin.update_user(user_info["sub"], user_data)[m
[32m+[m
[32m+[m[32m    if "errorCode" in user_update_response:[m
[32m+[m[32m        message = "Error During Update: " + user_update_response["errorSummary"][m
[32m+[m[32m    else:[m
[32m+[m[32m        message = "Thank you. Your Coupon was sent to your email on file!"[m
[32m+[m
[32m+[m[32m    return redirect([m
[32m+[m[32m        url_for([m
[32m+[m[32m            "consumerproducts_views_bp.consumerproducts_discounts",[m
[32m+[m[32m            _external="True",[m
[32m+[m[32m            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],[m
[32m+[m[32m            message=message))[m
[32m+[m
[32m+[m
[32m+[m[32m@consumerproducts_views_bp.route("/updateuserinfo", methods=["POST"])[m
[32m+[m[32m@is_authenticated[m
[32m+[m[32mdef consumerproducts_user_update():[m
[32m+[m[32m    logger.debug("consumerproducts_user_update")[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m[32m    user_id = request.form.get('user_id')[m
[32m+[m[32m    logging.debug(request.form.to_dict())[m
[32m+[m
[32m+[m[32m    first_name = safe_get_dict(request.form, 'firstname')[m
[32m+[m[32m    last_name = safe_get_dict(request.form, 'lastname')[m
[32m+[m[32m    email = safe_get_dict(request.form, 'email')[m
[32m+[m[32m    mobile_phone = safe_get_dict(request.form, 'mobilePhone')[m
[32m+[m[32m    consent = safe_get_dict(request.form, 'nconsent')[m
[32m+[m
[32m+[m[32m    user_data = {"profile": {[m
[32m+[m[32m        "firstName": first_name,[m
[32m+[m[32m        "lastName": last_name,[m
[32m+[m[32m        "email": email,[m
[32m+[m[32m        "mobilePhone": mobile_phone,[m
[32m+[m[32m        get_udp_ns_fieldname("consent"): consent,[m
[32m+[m[32m    }}[m
[32m+[m
[32m+[m[32m    logging.debug(user_data)[m
[32m+[m[32m    user_update_response = okta_admin.update_user(user_id, user_data)[m
[32m+[m[32m    logging.debug(user_update_response)[m
[32m+[m
[32m+[m[32m    if "error" in user_update_response:[m
[32m+[m[32m        message = "Error During Update: " + user_update_response[m
[32m+[m[32m    else:[m
[32m+[m[32m        message = "User Updated!"[m
[32m+[m
[32m+[m[32m    return redirect([m
[32m+[m[32m        url_for([m
[32m+[m[32m            "consumerproducts_views_bp.consumerproducts_profile",[m
[32m+[m[32m            _external="True",[m
[32m+[m[32m            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],[m
[32m+[m[32m            user_id=user_id,[m
[32m+[m[32m            message=message))[m
[32m+[m
[32m+[m
[32m+[m[32m@consumerproducts_views_bp.route("/updatecomm/<comm>")[m
[32m+[m[32m@is_authenticated[m
[32m+[m[32mdef consumerproducts_update_comm(comm):[m
[32m+[m[32m    logger.debug("consumerproducts_update_comm")[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m[32m    user_id = request.args.get('user_id')[m
[32m+[m[32m    logging.debug(user_id)[m
[32m+[m[32m    logging.debug(request.args.get('set'))[m
[32m+[m[32m    user_data = {"profile": {[m
[32m+[m[32m        get_udp_ns_fieldname(comm + "_comm"): request.args.get('set'),[m
[32m+[m[32m    }}[m
[32m+[m
[32m+[m[32m    logging.debug(user_data)[m
[32m+[m[32m    user_update_response = okta_admin.update_user(user_id, user_data)[m
[32m+[m[32m    logging.debug(user_update_response)[m
[32m+[m
[32m+[m[32m    if "errorCode" in user_update_response:[m
[32m+[m[32m        message = "Error During Update: " + user_update_response[m
[32m+[m[32m    else:[m
[32m+[m[32m        message = "Thank you! Your " + request.args.get('product') + " has been updated."[m
[32m+[m
[32m+[m[32m    return redirect([m
[32m+[m[32m        url_for([m
[32m+[m[32m            "consumerproducts_views_bp.consumerproducts_profile",[m
[32m+[m[32m            _external="True",[m
[32m+[m[32m            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],[m
[32m+[m[32m            user_id=user_id,[m
[32m+[m[32m            message=message))[m
[32m+[m
[32m+[m
[32m+[m[32m@consumerproducts_views_bp.route("/clearconsent/<userid>")[m
[32m+[m[32m@is_authenticated[m
[32m+[m[32mdef consumerproducts_clear_consent(userid):[m
[32m+[m[32m    logger.debug("consumerproducts_clear_consent")[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m
[32m+[m[32m    user_data = {"profile": {[m
[32m+[m[32m        get_udp_ns_fieldname("consent"): "",[m
[32m+[m[32m    }}[m
[32m+[m
[32m+[m[32m    user_update_response = okta_admin.update_application_user_profile(userid, user_data)[m
[32m+[m
[32m+[m[32m    if "error" in user_update_response:[m
[32m+[m[32m        message = "Error During Update: " + user_update_response["errorSummary"][m
[32m+[m[32m    else:[m
[32m+[m[32m        message = ""[m
[32m+[m
[32m+[m[32m    return redirect([m
[32m+[m[32m        url_for([m
[32m+[m[32m            "consumerproducts_views_bp.consumerproducts_profile",[m
[32m+[m[32m            _external="True",[m
[32m+[m[32m            _scheme=session[SESSION_INSTANCE_SETTINGS_KEY]["app_scheme"],[m
[32m+[m[32m            user_id=userid,[m
[32m+[m[32m            message=message))[m
[32m+[m
[32m+[m
[32m+[m[32m@consumerproducts_views_bp.route("/apps")[m
[32m+[m[32mdef consumerproducts_apps():[m
[32m+[m[32m    logger.debug("consumerproducts_apps")[m
[32m+[m[32m    okta_admin = OktaAdmin(session[SESSION_INSTANCE_SETTINGS_KEY])[m
[32m+[m[32m    app_info = okta_admin.get_applications_all()[m
[32m+[m[32m    logging.debug(app_info)[m
[32m+[m
[32m+[m[32m    return json.dumps(app_info)[m
[1mdiff --git a/app.py b/app.py[m
[1mindex 0f93af4..4de6ad1 100644[m
[1m--- a/app.py[m
[1m+++ b/app.py[m
[36m@@ -111,6 +111,9 @@[m [mapp.register_blueprint(ecommerce_views_bp, url_prefix='/ecommerce')[m
 from _b2b.views import b2b_views_bp[m
 app.register_blueprint(b2b_views_bp, url_prefix='/b2b')[m
 [m
[32m+[m[32m# consumerproducts theme[m
[32m+[m[32mfrom _consumerproducts.views import consumerproducts_views_bp[m
[32m+[m[32mapp.register_blueprint(consumerproducts_views_bp, url_prefix='/consumerproducts')[m
 [m
 ##############################################[m
 # Main Shared Routes[m
