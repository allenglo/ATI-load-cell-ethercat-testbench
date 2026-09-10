Set sh = CreateObject("WScript.Shell")
If sh.AppActivate(32732) Then
  WScript.Sleep 800
  keys = Array("%n","%n"," ","%n","%n","%n","%i","%n","%n","%f")
  For Each k In keys
    sh.SendKeys k
    WScript.Sleep 1100
  Next
  WScript.Echo "keys sent"
Else
  WScript.Echo "pid window not active"
End If
