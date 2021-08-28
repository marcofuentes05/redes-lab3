import org.jivesoftware.smack.*;
import org.jivesoftware.smack.packet.Message;

import java.util.*;
import java.io.File;
import java.io.FileNotFoundException;

class Main {
    static boolean connect(XMPPConnection con){
        try{
            con.connect();
            return true;
        }catch (Exception e){
            return false;
        }
    }
    static boolean login(XMPPConnection con, String userName, String password){
        try{
            con.login(userName, "redes");
            return true;
        }catch(Exception error){
            return false;
        }
    }
    static boolean sendMessage(XMPPConnection con, String user, String message){
        ChatManager c = con.getChatManager();
        Chat chat = c.createChat(user, null);
        try {
            chat.sendMessage(message);
            return true;
        }catch (Exception e){
            System.out.println(e.toString());
            return false;
        }
    }
    static boolean readFile(String fileName){
        try{
            File myFile = new File(fileName);
            Scanner myReader = new Scanner(myFile);
            while (myReader.hasNextLine()){
                String data = myReader.nextLine();
                System.out.println(data);
            }
        }catch (FileNotFoundException e){
            System.out.println("File not found");
        }
        return true;
    }
    public static void main(String args[]){
        XMPPConnection con = new XMPPConnection("alumchat.xyz");
        Map<String, ArrayList<String>> neighbours = new HashMap<>();
        neighbours.put("rodrigoa@alumchat.xyz", new ArrayList<String>(){{
            add("rodrigob@alumchat.xyz");
        }});
        neighbours.put("rodrigob@alumchat.xyz", new ArrayList<String>(){{
            add("rodrigoa@alumchat.xyz");
            add("rodrigoc@alumchat.xyz");
            add("rodrigod@alumchat.xyz");
        }});
        neighbours.put("rodrigoc@alumchat.xyz", new ArrayList<String>(){{
            add("rodrigob@alumchat.xyz");
            add("rodrigof@alumchat.xyz");
        }});
        neighbours.put("rodrigod@alumchat.xyz", new ArrayList<String>(){{
            add("rodrigob@alumchat.xyz");
            add("rodrigoe@alumchat.xyz");
        }});
        neighbours.put("rodrigoe@alumchat.xyz", new ArrayList<String>(){{
            add("rodrigod@alumchat.xyz");
            add("rodrigof@alumchat.xyz");
        }});
        neighbours.put("rodrigof@alumchat.xyz", new ArrayList<String>(){{
            add("rodrigoc@alumchat.xyz");
            add("rodrigoe@alumchat.xyz");
        }});
        if (connect(con)){
            Scanner optionScanner = new Scanner(System.in);
            System.out.println("Ingrese 1 para unirse a una estructura existente");
            System.out.println("Ingrese 2 para cargar una estructura nueva");
            System.out.println("Ingrese 3 para utilizar la estructura de prueba");
            String mainOption = optionScanner.nextLine();
            String userName = "rodrigoa@alumchat.xyz";
            String password = "redes";
            String topoFileName = "topo-1.txt";
            String namesFileName = "names-1.txt";
            String newNeighbours = "";
            if(mainOption.equals("1")){
                System.out.println("Ingrese nombre de usuario");
                userName = optionScanner.nextLine();
                System.out.println("Ingrese la contraseña");
                password = optionScanner.nextLine();
                System.out.println("Ingrese sus vecinos (separados por coma y sin espacios)");
                System.out.println("Ejemplo: abc18123@alumchat.xyz,bcd18321@alumchat.xyz");
                newNeighbours = optionScanner.nextLine();
            }else if (mainOption.equals("2")){
                System.out.println("Ingrese el nombre del archivo con la topología");
                topoFileName = optionScanner.nextLine();
                System.out.println("Ingrese el nombre del archivo con los nombres");
                namesFileName = optionScanner.nextLine();
                System.out.println("Ingrese nombre de usuario");
                userName = optionScanner.nextLine();
                System.out.println("Ingrese la contraseña");
                password = optionScanner.nextLine();
            }else if(mainOption.equals("3")){
                System.out.println("Ingrese el de usuario para hacer login");
                System.out.println("Opciones: rodrigoa@alumchat.xyz, rodrigob@alumchat.xyz...rodrigof@alumchat.xyz");
                System.out.println("No es necesario ingresar contraseña para estos usuarios, ya que únicamente son para pruebas");
                userName = optionScanner.nextLine();
            }
            ArrayList<String> seenMessages = new ArrayList<>();
            if (login(con, userName, password)) {
                ChatManager chatManager = con.getChatManager();
                String finalUserName = userName;
                Thread newThread = new Thread(()->{
                    /*
                    * Mensajes recibidos
                    * Posición  Descipción
                    * 0         Tipo de mensaje
                    * 1         Último emisor
                    * 2         Emisor original
                    * 3         Receptor final
                    * 4         Mensaje
                    * 5         UUID usado para ver si ya se vio este mensaje
                    * */
                    /* Mensajes para crear vecinos
                    * Posición  Descipción
                    * 0         Tipo de mensaje
                    * 1         Nombre de nuevo vecino
                    * */
                    chatManager.addChatListener(
                            new ChatManagerListener() {
                                @Override
                                public void chatCreated(Chat chat, boolean createdLocally) {
                                    chat.addMessageListener(new MessageListener() {
                                        //On message receivd, prints sender and message
                                        public void processMessage(Chat chat, Message msg) {
                                            if(msg.getBody() != null){
                                                String[] parts = msg.getBody().split("-");
                                                if(parts[0].equals("0")){
                                                    if(!seenMessages.contains(parts[5])){
                                                        if(finalUserName.equals(parts[3])){
                                                            System.out.println("Youve got mail");
                                                            seenMessages.add(parts[5]);
                                                            System.out.println(parts[2] + " : " + parts[4]);
                                                        }else{
                                                            seenMessages.add(parts[5]);
                                                            String newMessage = "0-" + finalUserName + "-" + parts[2] + "-" + parts[3] + "-" + parts[4] + "-" + parts[5];
                                                            for(String neighbour: neighbours.get(finalUserName)){
                                                                if(!parts[1].equals(neighbour)){
                                                                    sendMessage(con, neighbour, newMessage);
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                                else if (parts[0].equals("1")){
                                                    neighbours.get(finalUserName).add(parts[1]);
                                                }
                                            }
                                        }
                                    });
                                }
                            }
                    );
                });
                newThread.start();
                String optionInput = "";
                String receiver = "";
                String message = "";
                if(mainOption.equals("1")){
                    ArrayList<String> newNeighboursList = new ArrayList<>();
                    for (String newNeighbour :newNeighbours.split(",")){
                        sendMessage(con, newNeighbour, "1-"+userName);
                        newNeighboursList.add(newNeighbour);
                    }
                    neighbours.put(userName, newNeighboursList);
                }
                while (true){
                    System.out.println("Se inició sesión como " + userName);
                    System.out.println("Presione enter para enviar un mensaje");
                    optionInput = optionScanner.nextLine();
                    System.out.println("Ingrese el receptor de su mensaje");
                    receiver = optionScanner.nextLine();
                    System.out.println("Ingrese el mensaje a enviar");
                    message = optionScanner.nextLine();
                    String messageId = UUID.randomUUID().toString().replace("-", "_");
                    String finalMessage = "0-" + userName + "-" + userName + "-" + receiver + "-" + message + "-" + messageId;
                    seenMessages.add(messageId);
                    for(String contact:neighbours.get(userName)){
                        sendMessage(con, contact, finalMessage);
                    }
                    System.out.println("Enviado");
                }
            }
        }
    }
}