from time import sleep

from custom_logging import LogConfig
from RobotControl.RobotController import RobotController
from RobotControl.SSH import SSH
from RobotControl.InterpreterMode import InterpreterMode

recurring_logger = LogConfig.get_recurring_logger(__name__)
non_recurring_logger = LogConfig.get_non_recurring_logger(__name__)

class Robot:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Robot, cls).__new__(cls)
            cls._instance.__initialize(*args, **kwargs)
        return cls._instance

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance
    
    def __initialize(self):
        self.controller: RobotController = RobotController.get_instance()
        self.ssh: SSH = SSH.get_instance()
        self.interpreter_mode: InterpreterMode = InterpreterMode.get_instance()
        program_name = "eris_v2.urp"
        # Write program.urp to the robot
        self.ssh.write_file("/app/urprograms/eris_v2.urp", f"/programs/{program_name}")
        # self.ssh.write_file("RobotControl/program.urp", "../ursim/programs/program.urp")


        # robot.controller.send_popup(f"Forbereder scripts fra proxy: loader {program_name}")
        # sleep(1)
        # robot.controller.close_popup()
        self.controller.load_program(program_name)  # Sagde du ikke at load program ikke var nødvendigt på den fysiske robot?
        # Det er ikke nødvendigt for at få den til at opdatere scriptet, men vi skal bruge det for at switche den over til vores script.
        # Det virkede efter jeg satte den i remote control mode, men der sker ikke noget nu
            # Eventuelt hoppe på tableten og se om den har loaded det rigtige script,
            # Virkede power_on og break release?
        # Confirmed at den ikke har loaded det rigtige script.
            # Maybe ssh er cooked så. Det rigtige urp findes på robotten confirmed, og load_program skiftede "noget" robotten rebootede og safety settings skiftede, men indholdet af programmet er ikke ændret.
        # Jeg laver en manuel urp ligesom vi gjorde i fredags og så tager vi den derfra
        # jeg har saved den som eris_v2.urp, vil du lige scp den over for mig?
            # I'll try

        # no nothing
            # Hvor er koden, som bliver kørt, når du clicker på debug knappen?

        # Kan du se på tableten, om der er et script på robotten der starter.
        # For ved ikke, om den ikke player scriptet, eller om det den player ikke rent faktisk har scriptet.
            # Har ændret
        # Har tilføjet, at den skriver til log, alt efter hvilket response den får, når du prøver at sende noget over dashboards serveren.
        # Prøv at genstarte proxy

        # Den bevæger sig nu. Jeg ved ikke hvorfor
            # Må være når vi loader urp filen, så bliver den ikke loaded rigtig. Du ved ligesom når en pc bare skal genstartes
            # Kan ikke se mig til, hvad der skulle have fixed den, udover at den bare fixede sig selv, efter at vi docker compose down --> docker compose up.

        # BRATAN LÆS LOGS, der stpr "Failed to execute play"
        # Forstår ikke, der står failed to play, men loggen lige inden, der står der "Starting program"

        # tabletten viser stadig status running btw. Måske er programmet slet ikke stoppet?
            # Probably that. Har du "halt" til sidst i urp filshhhhhhhhhhhhen?
                # What xd?
        # jeg havde glemt halt. med halt virker det bare.  sick nok
        
        # Vi har fundet ud af, at fixen er at force load 3 gange og eventually virker det bare? Like what

        # Jeg ved stadig ikke helt med de der urp filer hvad der er op og ned, men jeg tror godt at vi kan få det til at køre.
        # har du fundet noget med logs til errors?
            # Nope kunne ikke finde noget, men prøver lige at kigge igen

        # Jeg kan lave en filezilla søgning på .log igen hvis du vil have det?
        # og ellers kan det være at du skal se på den gamle kode til at aflæse det fra primary socket? og prøve det på den fysiske robot
                # På den gamle kode readede vi ikke error logs, vi kiggede blot på robottens stadie og prøvede at elicit hvad der kunne være galt
                # jeg tænker på det eksperiment som du havde hvor den ikke sendte de rigtige beskeder

        # Du kan ikke lige få den til at få en type error? Bare ved at sætte a=2 og så a="hi"
            # Jeg har en type error popup på polyscope skærmen right now


        # found it /tmp/log/urcontrol/current
        # Sætter du den så ind det rigtige sted i koden?
            # ye
        # så kan jeg også når vi er færdige lave et symlink i containeren ligesom programs

        # Der kan være et problem med, at der er mere i den her log, så mit read_logs ikke virker.
            # Currently, læser jeg de sidste 3 linjer I loggen, men I den her log, er der en masse logs med, at Custom Socket er destroyed
            # Jeg kan scp den over på min pc så du har den til future reference?
                # Ye could be nice

        # what now, skal du lige have 5-10 min til at forsøge at læse fra den nye log eller skal vi hoppe over på den nyeste branch og tjekke at alt virker?
            # hop over på den nye branch, og se om det bare virker
                # Vi skal dog lige change 2 ting
                # 1. At vi writer den rigtige urp fil, eller commenter det med at den writer en urp fil
                # 2. Tror constants.py med ssh_username er forkert, da jeg troede username var robot, men det er root på den physical
                # constants.py har bare en default til hvis vi ikke specificerer det i docker-compose env. Den bør læse fra env. Det kræver bare en hel docker compose down og up for at opdatere env. restart container er ikke nok
                    # I see, så burde det virke z



        non_recurring_logger.info("Waiting for program to load")
        sleep(5)
        self.controller.power_on()
        non_recurring_logger.info("Waiting for robot to power on")
        sleep(5)
        self.controller.brake_release()
        non_recurring_logger.info("Waiting for brake release")
        sleep(2)
    