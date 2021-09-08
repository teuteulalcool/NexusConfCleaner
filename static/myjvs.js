function zeAlert() {
    alert("Alerte!!!")
 }

 function HideShow() {
   var x = document.getElementById("HideTable");
   if (x.style.display === "none") {
     x.style.display = "block";
   } else {
     x.style.display = "none";
   }
 } 

 function CheckUncheckAll(){
    var  selectAllCheckbox=document.getElementById("checkUncheckAll");
    if(selectAllCheckbox.checked==true){
     var checkboxes =  document.getElementsByName("files");
      for(var i=0, n=checkboxes.length;i<n;i++) {
       checkboxes[i].checked = true;
      }
      var checkboxes =  document.getElementsByName("vrf");
      for(var i=0, n=checkboxes.length;i<n;i++) {
       checkboxes[i].checked = true;
      }
     }else {
      var checkboxes =  document.getElementsByName("files");
      for(var i=0, n=checkboxes.length;i<n;i++) {
       checkboxes[i].checked = false;
      }
      var checkboxes =  document.getElementsByName("vrf");
      for(var i=0, n=checkboxes.length;i<n;i++) {
       checkboxes[i].checked = false;
      }
     }
    }