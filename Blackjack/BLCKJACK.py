try:
 import BLCKJACM
except ImportError as e:
 if 'BLCKJACM' not in str(e):raise
 print("BLCKJACM.8mp2 is missing.")
 print("Send it to the calculator.")
