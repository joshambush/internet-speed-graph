"""
	|****************************|
	|Author:Josh Ambush
	|https://github.com/joshambush/
	| joshambush5435@gmail.com
	|by-: joshambush
	|______________________________|
	"""

from PyQt4 import QtGui, QtCore, uic
import os, sys, ping, time, rrd, signal

host = "192.168.1.102"
rrdfile = "temp/ping.rrd"
rrdpng = "temp/ping.png"

default_graph_width = 400
default_graph_height = 100



class GrapherApp(QtGui.QMainWindow):
	def __init__(self):
		QtGui.QMainWindow.__init__(self)
		f = open('resources/darkorange.stylesheet', 'r')
		self.styleData = f.read()
		f.close()
		self.ui = uic.loadUi('app.ui') 
		self.ui.ms_label.setText("Waiting...")
		self.ui.setStyleSheet(self.styleData)
		self.ui.show()
		#self.ui.showFullScreen()
		
		rrd_thread.set_graph_size(self.ui.graph.size().width(), self.ui.graph.size().height())
		
		self.connect(ping_thread, ping_thread.signal, self.updateUI)
		self.connect(self.ui.exitButton, QtCore.SIGNAL("clicked()"), exit)
		
	def updateUI(self, value):
                
                if value == "nan":
			win.ui.ms_label.setStyleSheet("color: rgb(255,0, 0);")
			win.ui.ms_label.setText("Router is Down")
		#elif value == "nan":
                        #win.ui.ms_label.setStyleSheet("color: rgb(155,0, 0);")
                        #win.ui.ms_label.setText("")
                else:
                        win.ui.ms_label.setStyleSheet("color: rgb(0, 255, 0);")
                        win.ui.ms_label.setText("Router: "  + value + " ms")
		win.ui.graph.setPixmap(QtGui.QPixmap(os.getcwd() + "/" + rrdpng))


class PingThread(QtCore.QThread):
   def __init__(self):
      QtCore.QThread.__init__(self, parent=app)
      self.signal = QtCore.SIGNAL("ping_signal")
	
   def run(self):
      while True:
         try:
            pingval = ping.ping(host)
         except:
            pingval = {'minping': -1, 'avgping': -1, 'timeout': True}
			
         rrd.update_rrd(rrdfile, pingval)
			
         self.emit( rrd_thread.signal, pingval )
         self.emit( self.signal, str( round( float(pingval['minping']), 2 ) ) )
			
         time.sleep(1)


class RRDThread(QtCore.QThread):
   def __init__(self):
      QtCore.QThread.__init__(self, parent=app)
      self.signal = QtCore.SIGNAL("rrd_png_update_signal")
      self.graph_width = default_graph_width
      self.graph_height = default_graph_height
	
   def run(self):
      self.connect(ping_thread, rrd_thread.signal, self.update_png)
		
   def update_png(self, pingval):
      rrd.update_png(rrdpng, rrdfile, self.graph_width, self.graph_height)
	
   def set_graph_size(self, width, height):
      self.graph_width = int(width)
      self.graph_height = int(height)


def exit():
   sys.exit(0)

def signal_handler(signal, frame):
   sys.exit(0)

if __name__ == "__main__":
   signal.signal(signal.SIGINT, signal_handler)
	
   rrd.remove_png(rrdpng)
   rrd.create_rrd(rrdfile)
	
   app = QtGui.QApplication(sys.argv)
   app.setStyle('plastique')
	
   ping_thread = PingThread()
   rrd_thread = RRDThread()
	
   win = GrapherApp()
		
   ping_thread.start()
   rrd_thread.start()
	
   sys.exit(app.exec_())
