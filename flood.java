import org.jivesoftware.smack.*;
import org.jivesoftware.smack.packet.Message;

import java.util.*;

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
            String userName = "rodrigoe@alumchat.xyz";
            ArrayList<String> seenMessages = new ArrayList<>();
            if (login(con, userName, "redes")) {
                ChatManager chatManager = con.getChatManager();
                Thread newThread = new Thread(()->{
                    /*
                    * Mensajs recibidos
                    * 0 es el último emisor
                    * 1 es el emisor original
                    * 2 es el receptor final
                    * 3 es el mensaje
                    * 4 es el uuid, usado para ver si ya se vio este mensaje
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
                                                if(!seenMessages.contains(parts[4])){
                                                    if(userName.equals(parts[2])){
                                                        System.out.println("Youve got mail");
                                                        seenMessages.add(parts[4]);
                                                        System.out.println(chat.getParticipant() + " : " + parts[3]);
                                                    }else{
                                                        seenMessages.add(parts[4]);
                                                        String newMessage = userName + "-" + parts[1] + "-" + parts[2] + "-" + parts[3] + "-" + parts[4];
                                                        for(String neighbour: neighbours.get(userName)){
                                                            if(!parts[0].equals(neighbour)){
                                                                sendMessage(con, neighbour, newMessage);
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    });
                                }
                            }
                    );
                });
                newThread.start();
                System.out.println(userName.toString());
                System.out.println("now");
                Scanner optionScanner = new Scanner(System.in);
                String optionInput = "";
                String receiver = "";
                String message = "";
                while (true){
                    System.out.println("Presione enter para enviar un mensaje");
                    optionInput = optionScanner.nextLine();
                    System.out.println("Ingrese el receptor de su mensaje");
                    receiver = optionScanner.nextLine();
                    System.out.println("Ingrese el mensaje a enviar");
                    message = optionScanner.nextLine();
                    String messageId = UUID.randomUUID().toString().replace("-", "_");
                    String finalMessage = userName + "-" + userName + "-" + receiver + "-" + message + "-" + messageId;
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