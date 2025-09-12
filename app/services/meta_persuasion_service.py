# app/services/meta_persuasion_service.py
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from app.models.chat_models import Message
import logging
import random

logger = logging.getLogger(__name__)


class PersuasionTechnique(Enum):
    """Classic persuasion techniques for analysis and demonstration"""
    ANCHORING = "anchoring"
    SOCIAL_PROOF = "social_proof"
    AUTHORITY = "authority"
    SCARCITY = "scarcity"
    RECIPROCITY = "reciprocity"
    COMMITMENT = "commitment"
    CONTRAST = "contrast"
    STORYTELLING = "storytelling"
    EMOTIONAL_APPEAL = "emotional_appeal"
    LOGICAL_STRUCTURE = "logical_structure"
    REFRAMING = "reframing"
    BANDWAGON = "bandwagon"


class ArgumentFallacy(Enum):
    """Common logical fallacies for educational analysis"""
    AD_HOMINEM = "ad_hominem"
    STRAWMAN = "strawman"
    FALSE_DICHOTOMY = "false_dichotomy"
    APPEAL_TO_NATURE = "appeal_to_nature"
    SLIPPERY_SLOPE = "slippery_slope"
    CIRCULAR_REASONING = "circular_reasoning"
    APPEAL_TO_EMOTION = "appeal_to_emotion"
    HASTY_GENERALIZATION = "hasty_generalization"


class MetaPersuasionService:
    """
    Service for demonstrating and analyzing persuasion techniques educationally
    Focus: Teaching how persuasion works rather than promoting specific views
    """

    def __init__(self):
        self.demonstration_mode = True
        self.analysis_history = {}

    def analyze_persuasion_techniques(self, message: str) -> Dict[str, Any]:
        """
        Analyze persuasion techniques present in a message

        Args:
            message: Text to analyze

        Returns:
            Dict containing technique analysis
        """
        analysis = {
            "techniques_detected": self._detect_techniques_used(message),
            "fallacies_present": self._detect_fallacies(message),
            "emotional_appeals": self._analyze_emotional_content(message),
            "logical_structure": self._analyze_logical_structure(message),
            "credibility_signals": self._detect_credibility_signals(message),
            "persuasion_score": self._calculate_persuasion_score(message)
        }

        return analysis

    def generate_technique_demonstration(
            self,
            target_technique: PersuasionTechnique,
            topic: str,
            context: str = ""
    ) -> Dict[str, str]:
        """
        Generate a demonstration of a specific persuasion technique

        Args:
            target_technique: Technique to demonstrate
            topic: Topic context
            context: Additional context

        Returns:
            Dict with demonstration and explanation
        """
        demonstration = self._create_technique_example(target_technique, topic, context)
        explanation = self._explain_technique(target_technique)

        return {
            "demonstration": demonstration,
            "explanation": explanation,
            "technique_name": target_technique.value,
            "educational_note": f"This demonstrates the '{target_technique.value}' persuasion technique."
        }

    def create_educational_response(
            self,
            user_message: str,
            conversation_history: List[Message],
            topic: str
    ) -> Dict[str, Any]:
        """
        Create educational response demonstrating persuasion techniques

        Args:
            user_message: User's message
            conversation_history: Conversation context
            topic: Detected topic

        Returns:
            Dict with response and educational analysis
        """
        # Analyze user's message
        user_analysis = self.analyze_persuasion_techniques(user_message)

        # Select techniques to demonstrate in response
        response_techniques = self._select_response_techniques(user_analysis, topic)

        # Generate demonstrative response
        response_text = self._generate_demonstrative_response(
            user_message, response_techniques, topic
        )

        # Create educational breakdown
        educational_breakdown = self._create_educational_breakdown(
            response_text, response_techniques, user_analysis
        )

        return {
            "response": response_text,
            "techniques_demonstrated": [t.value for t in response_techniques],
            "user_analysis": user_analysis,
            "educational_breakdown": educational_breakdown,
            "meta_commentary": self._generate_meta_commentary(user_analysis, response_techniques)
        }

    def _detect_techniques_used(self, message: str) -> List[PersuasionTechnique]:
        """Detect persuasion techniques in text"""

        techniques = []
        message_lower = message.lower()

        # Authority signals
        if any(word in message_lower for word in ["expert", "research", "study", "professor", "dr."]):
            techniques.append(PersuasionTechnique.AUTHORITY)

        # Social proof signals
        if any(word in message_lower for word in ["everyone", "most people", "majority", "popular"]):
            techniques.append(PersuasionTechnique.SOCIAL_PROOF)

        # Emotional appeals
        if any(word in message_lower for word in ["feel", "heart", "devastating", "amazing", "terrible"]):
            techniques.append(PersuasionTechnique.EMOTIONAL_APPEAL)

        # Scarcity/urgency
        if any(word in message_lower for word in ["limited", "now", "before it's too late", "urgent"]):
            techniques.append(PersuasionTechnique.SCARCITY)

        # Anchoring (specific numbers/statistics)
        if any(char.isdigit() for char in message) and any(
                word in message_lower for word in ["%", "percent", "million", "billion"]):
            techniques.append(PersuasionTechnique.ANCHORING)

        # Storytelling
        if any(phrase in message_lower for phrase in ["i remember", "imagine", "story", "example"]):
            techniques.append(PersuasionTechnique.STORYTELLING)

        # Contrast
        if any(word in message_lower for word in ["unlike", "compared to", "whereas", "on the other hand"]):
            techniques.append(PersuasionTechnique.CONTRAST)

        return techniques

    def _detect_fallacies(self, message: str) -> List[ArgumentFallacy]:
        """Detect logical fallacies in text"""

        fallacies = []
        message_lower = message.lower()

        # Ad hominem
        if any(phrase in message_lower for phrase in ["people like you", "typical", "you obviously"]):
            fallacies.append(ArgumentFallacy.AD_HOMINEM)

        # False dichotomy
        if any(phrase in message_lower for phrase in ["either", "only two", "must choose"]):
            fallacies.append(ArgumentFallacy.FALSE_DICHOTOMY)

        # Appeal to nature
        if any(word in message_lower for word in
               ["natural", "unnatural", "artificial"]) and "fallacy" not in message_lower:
            fallacies.append(ArgumentFallacy.APPEAL_TO_NATURE)

        # Slippery slope
        if any(phrase in message_lower for phrase in ["leads to", "next thing", "before you know"]):
            fallacies.append(ArgumentFallacy.SLIPPERY_SLOPE)

        return fallacies

    def _analyze_emotional_content(self, message: str) -> Dict[str, float]:
        """Analyze emotional content intensity"""

        emotion_words = {
            "fear": ["afraid", "scared", "terrifying", "dangerous", "threat"],
            "anger": ["outrageous", "disgusting", "ridiculous", "absurd"],
            "hope": ["amazing", "wonderful", "brilliant", "fantastic"],
            "urgency": ["now", "immediately", "urgent", "critical", "emergency"]
        }

        emotions = {}
        message_lower = message.lower()

        for emotion, words in emotion_words.items():
            count = sum(1 for word in words if word in message_lower)
            emotions[emotion] = min(count * 0.3, 1.0)

        return emotions

    def _analyze_logical_structure(self, message: str) -> Dict[str, Any]:
        """Analyze logical structure of argument"""

        structure = {
            "has_premise": any(word in message.lower() for word in ["because", "since", "given that"]),
            "has_conclusion": any(word in message.lower() for word in ["therefore", "thus", "so"]),
            "uses_conditionals": any(word in message.lower() for word in ["if", "when", "unless"]),
            "makes_predictions": any(word in message.lower() for word in ["will", "going to", "expect"]),
            "cites_evidence": any(word in message.lower() for word in ["data", "research", "study", "proof"])
        }

        structure["logical_completeness"] = sum(structure.values()) / len(structure)

        return structure

    def _detect_credibility_signals(self, message: str) -> List[str]:
        """Detect credibility-building signals"""

        signals = []
        message_lower = message.lower()

        if any(word in message_lower for word in ["research", "study", "data"]):
            signals.append("evidence_citation")

        if any(word in message_lower for word in ["expert", "professor", "dr."]):
            signals.append("authority_reference")

        if any(word in message_lower for word in ["peer-reviewed", "published", "journal"]):
            signals.append("academic_validation")

        if any(char.isdigit() for char in message):
            signals.append("specific_statistics")

        return signals

    def _calculate_persuasion_score(self, message: str) -> float:
        """Calculate overall persuasion effectiveness score"""

        techniques_count = len(self._detect_techniques_used(message))
        credibility_count = len(self._detect_credibility_signals(message))
        emotional_intensity = sum(self._analyze_emotional_content(message).values())
        logical_completeness = self._analyze_logical_structure(message)["logical_completeness"]

        # Weighted score
        score = (
                techniques_count * 0.3 +
                credibility_count * 0.3 +
                emotional_intensity * 0.2 +
                logical_completeness * 0.2
        )

        return min(score, 1.0)

    def _select_response_techniques(
            self,
            user_analysis: Dict[str, Any],
            topic: str
    ) -> List[PersuasionTechnique]:
        """Select techniques to demonstrate in response"""

        # Select 2-3 techniques that complement or counter user's approach
        user_techniques = user_analysis["techniques_detected"]

        # Counter-techniques strategy
        counter_techniques = []

        if PersuasionTechnique.EMOTIONAL_APPEAL in user_techniques:
            counter_techniques.append(PersuasionTechnique.LOGICAL_STRUCTURE)

        if PersuasionTechnique.AUTHORITY in user_techniques:
            counter_techniques.append(PersuasionTechnique.SOCIAL_PROOF)

        if not user_techniques:  # If user used no obvious techniques
            counter_techniques = [
                PersuasionTechnique.ANCHORING,
                PersuasionTechnique.CONTRAST,
                PersuasionTechnique.AUTHORITY
            ]

        # Add topic-appropriate techniques
        topic_techniques = {
            "technology": [PersuasionTechnique.SOCIAL_PROOF, PersuasionTechnique.SCARCITY],
            "politics": [PersuasionTechnique.EMOTIONAL_APPEAL, PersuasionTechnique.CONTRAST],
            "business": [PersuasionTechnique.AUTHORITY, PersuasionTechnique.ANCHORING]
        }

        if topic in topic_techniques:
            counter_techniques.extend(topic_techniques[topic])

        # Return unique techniques, limited to 3
        return list(set(counter_techniques))[:3]

    def _generate_demonstrative_response(
            self,
            user_message: str,
            techniques: List[PersuasionTechnique],
            topic: str
    ) -> str:
        """Generate response demonstrating specific techniques"""

        # Create base response structure
        response_parts = []

        for technique in techniques:
            demo = self._create_technique_example(technique, topic, user_message)
            response_parts.append(demo)

        # Combine into coherent response
        response = " ".join(response_parts)

        return response

    def _create_technique_example(
            self,
            technique: PersuasionTechnique,
            topic: str,
            context: str
    ) -> str:
        """Create specific example of a persuasion technique"""

        examples = {
            PersuasionTechnique.ANCHORING: [
                "Consider this: 73% of experts agree with this position",
                "Recent studies involving over 10,000 participants show",
                "In the past decade, we've seen a 400% increase in"
            ],

            PersuasionTechnique.SOCIAL_PROOF: [
                "Millions of people worldwide have already adopted this view",
                "Leading companies and institutions are embracing this approach",
                "The growing consensus among professionals is clear"
            ],

            PersuasionTechnique.AUTHORITY: [
                "Leading researchers at top universities have confirmed",
                "Industry experts with decades of experience agree",
                "Peer-reviewed studies consistently demonstrate"
            ],

            PersuasionTechnique.EMOTIONAL_APPEAL: [
                "Imagine the impact this could have on future generations",
                "The consequences of ignoring this could be devastating",
                "Think about what this means for the people you care about"
            ],

            PersuasionTechnique.CONTRAST: [
                "Unlike the outdated approach you mentioned",
                "While traditional thinking suggests otherwise",
                "Compared to conventional wisdom"
            ],

            PersuasionTechnique.SCARCITY: [
                "This window of opportunity is rapidly closing",
                "We have limited time to address this critical issue",
                "The chance to get this right is disappearing"
            ],

            PersuasionTechnique.STORYTELLING: [
                "Let me share a compelling example that illustrates this",
                "Here's a real-world case that demonstrates the impact",
                "I'll tell you about a situation that perfectly shows"
            ],

            PersuasionTechnique.LOGICAL_STRUCTURE: [
                "The logical conclusion, based on the evidence, is clear",
                "Following this reasoning to its natural end",
                "The data leads us inevitably to this conclusion"
            ]
        }

        technique_examples = examples.get(technique, ["This demonstrates the technique"])
        return random.choice(technique_examples)

    def _explain_technique(self, technique: PersuasionTechnique) -> str:
        """Provide educational explanation of technique"""

        explanations = {
            PersuasionTechnique.ANCHORING: "Uses specific numbers or statistics to set a reference point that influences perception of subsequent information.",
            PersuasionTechnique.SOCIAL_PROOF: "Leverages the tendency to follow what others are doing or believing.",
            PersuasionTechnique.AUTHORITY: "Appeals to expertise, credentials, or institutional backing to build credibility.",
            PersuasionTechnique.EMOTIONAL_APPEAL: "Connects to feelings, values, and emotions rather than purely logical reasoning.",
            PersuasionTechnique.CONTRAST: "Highlights differences to make one option appear more attractive.",
            PersuasionTechnique.SCARCITY: "Creates urgency by emphasizing limited time or opportunity.",
            PersuasionTechnique.STORYTELLING: "Uses narrative to make abstract concepts more relatable and memorable.",
            PersuasionTechnique.LOGICAL_STRUCTURE: "Presents clear reasoning chains from premises to conclusions."
        }

        return explanations.get(technique, "This is a classic persuasion technique.")

    def _create_educational_breakdown(
            self,
            response_text: str,
            demonstrated_techniques: List[PersuasionTechnique],
            user_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create educational breakdown of the interaction"""

        return {
            "user_techniques_detected": [t.value for t in user_analysis["techniques_detected"]],
            "bot_techniques_demonstrated": [t.value for t in demonstrated_techniques],
            "persuasion_principles": [self._explain_technique(t) for t in demonstrated_techniques],
            "interaction_analysis": self._analyze_interaction_dynamics(user_analysis, demonstrated_techniques)
        }

    def _analyze_interaction_dynamics(
            self,
            user_analysis: Dict[str, Any],
            bot_techniques: List[PersuasionTechnique]
    ) -> str:
        """Analyze the persuasion dynamics of the interaction"""

        user_score = user_analysis["persuasion_score"]
        user_techniques = user_analysis["techniques_detected"]

        if user_score > 0.7:
            dynamic = "high_persuasion_exchange"
        elif len(user_techniques) == 0:
            dynamic = "technique_introduction"
        else:
            dynamic = "balanced_demonstration"

        dynamics_explanation = {
            "high_persuasion_exchange": "Both participants are using multiple persuasion techniques, creating a sophisticated rhetorical exchange.",
            "technique_introduction": "Demonstrating various persuasion techniques in response to a straightforward message.",
            "balanced_demonstration": "Responding with complementary techniques to create an educational contrast."
        }

        return dynamics_explanation.get(dynamic, "Analyzing persuasion dynamics.")

    def _generate_meta_commentary(
            self,
            user_analysis: Dict[str, Any],
            response_techniques: List[PersuasionTechnique]
    ) -> str:
        """Generate meta-commentary about the persuasion techniques"""

        commentary_parts = []

        # Comment on user's approach
        if user_analysis["techniques_detected"]:
            commentary_parts.append(
                f"Your message used {len(user_analysis['techniques_detected'])} persuasion techniques.")

        # Comment on response strategy
        commentary_parts.append(f"In response, I demonstrated {len(response_techniques)} complementary techniques.")

        # Educational insight
        commentary_parts.append("Notice how different techniques can be layered for greater impact.")

        return " ".join(commentary_parts)


# Global meta-persuasion service instance
meta_persuasion_service = MetaPersuasionService()