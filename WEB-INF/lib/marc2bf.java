/*
  marc2bf.java is a Java Gateway class for using the Saxon XQuery 

*/
import py4j.GatewayServer;
import net.sf.saxon;

public class marc2bf {

  public static void main(String[] args) {
    GatewayServer gatewayServer = new GatewayServer();
    gatewayServer.start();
    System.out.println("Gateway Server Started");
  }

}
