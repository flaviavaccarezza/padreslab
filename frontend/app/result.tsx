import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  Modal,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import * as Clipboard from 'expo-clipboard';
import { type SituationResponse, rewriteMessage, type RewriteResponse } from '../utils/api';

export default function ResultScreen() {
  const router = useRouter();
  const params = useLocalSearchParams();
  const [rewriteModalVisible, setRewriteModalVisible] = useState(false);
  const [rewriteText, setRewriteText] = useState('');
  const [rewriteLoading, setRewriteLoading] = useState(false);
  const [rewriteResult, setRewriteResult] = useState<RewriteResponse | null>(null);

  const response: SituationResponse = params.responseData
    ? JSON.parse(params.responseData as string)
    : null;

  if (!response) {
    return (
      <SafeAreaView style={styles.container}>
        <Text>Error: No se encontraron datos</Text>
      </SafeAreaView>
    );
  }

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case 'baja':
        return '#10b981';
      case 'media':
        return '#f59e0b';
      case 'alta':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  const handleCopy = async () => {
    const text = `
PadresLab - Orientación

Intensidad: ${response.intensidad_emocional}

${response.riesgo_alto && response.mensaje_ayuda_profesional ? `⚠️ IMPORTANTE: ${response.mensaje_ayuda_profesional}\n\n` : ''}
✨ QUÉ PODRÍA ESTAR PASANDO
${response.secciones.que_podria_estar_pasando}

💬 CÓMO HABLAR
Frases sugeridas:
${response.secciones.como_hablar.frases_sugeridas.map(f => `• ${f}`).join('\n')}

Qué evitar:
${response.secciones.como_hablar.que_evitar.map(e => `• ${e}`).join('\n')}

Tono recomendado: ${response.secciones.como_hablar.tono_recomendado}

⚠️ SEÑALES DE ALERTA
Signos a observar:
${response.secciones.senales_de_alerta.signos.map(s => `• ${s}`).join('\n')}

Cuándo actuar: ${response.secciones.senales_de_alerta.cuando_actuar}

🎯 PRÓXIMOS PASOS
Qué hacer ahora: ${response.secciones.proximos_pasos.que_hacer_ahora}

Qué observar:
${response.secciones.proximos_pasos.que_observar.map(o => `• ${o}`).join('\n')}

Cómo seguir: ${response.secciones.proximos_pasos.como_seguir}

❤️ RECONEXIÓN
Preguntas para reconstruir:
${response.secciones.reconexion.preguntas.map(p => `• ${p}`).join('\n')}

Actividades sugeridas:
${response.secciones.reconexion.actividades.map(a => `• ${a}`).join('\n')}
    `.trim();

    await Clipboard.setStringAsync(text);
    Alert.alert('¡Copiado!', 'La orientación se copió al portapapeles');
  };

  const handleRewrite = async () => {
    if (!rewriteText.trim()) {
      Alert.alert('Atención', 'Por favor escribe el mensaje que quieres reescribir');
      return;
    }

    setRewriteLoading(true);
    try {
      const result = await rewriteMessage({ original_text: rewriteText });
      setRewriteResult(result);
    } catch (error) {
      Alert.alert('Error', 'No pudimos reescribir el mensaje');
    } finally {
      setRewriteLoading(false);
    }
  };

  const copyRewriteVersion = async (version: string) => {
    await Clipboard.setStringAsync(version);
    Alert.alert('¡Copiado!', 'La versión se copió al portapapeles');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <TouchableOpacity onPress={() => router.back()} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color="#374151" />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Orientación</Text>
          <View style={{ width: 24 }} />
        </View>

        <View style={styles.intensitySection}>
          <Text style={styles.intensityLabel}>Intensidad emocional:</Text>
          <View
            style={[
              styles.intensityBadge,
              { backgroundColor: getIntensityColor(response.intensidad_emocional) },
            ]}
          >
            <Text style={styles.intensityText}>{response.intensidad_emocional.toUpperCase()}</Text>
          </View>
        </View>

        {response.riesgo_alto && response.mensaje_ayuda_profesional && (
          <View style={styles.warningBox}>
            <Ionicons name="warning" size={24} color="#dc2626" />
            <Text style={styles.warningTitle}>IMPORTANTE</Text>
            <Text style={styles.warningText}>{response.mensaje_ayuda_profesional}</Text>
            <TouchableOpacity
              style={styles.warningButton}
              onPress={() => router.push('/help' as any)}
            >
              <Text style={styles.warningButtonText}>Ver recursos de ayuda</Text>
            </TouchableOpacity>
          </View>
        )}

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>✨ Qué podría estar pasando</Text>
          <Text style={styles.sectionText}>{response.secciones.que_podria_estar_pasando}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>💬 Cómo hablar</Text>
          <Text style={styles.subsectionTitle}>Frases sugeridas:</Text>
          {response.secciones.como_hablar.frases_sugeridas.map((frase, index) => (
            <Text key={index} style={styles.bulletItem}>• {frase}</Text>
          ))}
          <Text style={styles.subsectionTitle}>Qué evitar:</Text>
          {response.secciones.como_hablar.que_evitar.map((evitar, index) => (
            <Text key={index} style={styles.bulletItem}>• {evitar}</Text>
          ))}
          <Text style={styles.subsectionTitle}>Tono recomendado:</Text>
          <Text style={styles.sectionText}>{response.secciones.como_hablar.tono_recomendado}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>⚠️ Señales de alerta</Text>
          <Text style={styles.subsectionTitle}>Signos a observar:</Text>
          {response.secciones.senales_de_alerta.signos.map((signo, index) => (
            <Text key={index} style={styles.bulletItem}>• {signo}</Text>
          ))}
          <Text style={styles.subsectionTitle}>Cuándo actuar:</Text>
          <Text style={styles.sectionText}>{response.secciones.senales_de_alerta.cuando_actuar}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>🎯 Próximos pasos</Text>
          <Text style={styles.subsectionTitle}>Qué hacer ahora:</Text>
          <Text style={styles.sectionText}>{response.secciones.proximos_pasos.que_hacer_ahora}</Text>
          <Text style={styles.subsectionTitle}>Qué observar:</Text>
          {response.secciones.proximos_pasos.que_observar.map((observar, index) => (
            <Text key={index} style={styles.bulletItem}>• {observar}</Text>
          ))}
          <Text style={styles.subsectionTitle}>Cómo seguir:</Text>
          <Text style={styles.sectionText}>{response.secciones.proximos_pasos.como_seguir}</Text>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>❤️ Reconexión</Text>
          <Text style={styles.subsectionTitle}>Preguntas para reconstruir confianza:</Text>
          {response.secciones.reconexion.preguntas.map((pregunta, index) => (
            <Text key={index} style={styles.bulletItem}>• {pregunta}</Text>
          ))}
          <Text style={styles.subsectionTitle}>Actividades sugeridas:</Text>
          {response.secciones.reconexion.actividades.map((actividad, index) => (
            <Text key={index} style={styles.bulletItem}>• {actividad}</Text>
          ))}
        </View>

        <View style={styles.actionButtons}>
          <TouchableOpacity style={styles.copyButton} onPress={handleCopy}>
            <Ionicons name="copy" size={20} color="#fff" />
            <Text style={styles.copyButtonText}>Copiar todo</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.rewriteButton}
            onPress={() => setRewriteModalVisible(true)}
          >
            <Ionicons name="create" size={20} color="#6366f1" />
            <Text style={styles.rewriteButtonText}>Reescribir mensaje</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.backHomeButton} onPress={() => router.back()}>
          <Text style={styles.backHomeButtonText}>Nueva consulta</Text>
        </TouchableOpacity>
      </ScrollView>

      <Modal
        visible={rewriteModalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setRewriteModalVisible(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Reescribir lo que quiero decir</Text>
              <TouchableOpacity onPress={() => {
                setRewriteModalVisible(false);
                setRewriteResult(null);
                setRewriteText('');
              }}>
                <Ionicons name="close" size={24} color="#374151" />
              </TouchableOpacity>
            </View>

            <ScrollView style={styles.modalScroll}>
              <Text style={styles.modalLabel}>Escribe el mensaje que quieres decirle a tu hijo/a:</Text>
              <TextInput
                style={styles.modalInput}
                multiline
                numberOfLines={4}
                value={rewriteText}
                onChangeText={setRewriteText}
                placeholder="Ej: Estoy muy enojado porque llegaste tarde otra vez..."
                placeholderTextColor="#999"
                textAlignVertical="top"
              />

              <TouchableOpacity
                style={[styles.modalButton, rewriteLoading && styles.buttonDisabled]}
                onPress={handleRewrite}
                disabled={rewriteLoading}
              >
                {rewriteLoading ? (
                  <ActivityIndicator color="#fff" />
                ) : (
                  <Text style={styles.modalButtonText}>Reescribir</Text>
                )}
              </TouchableOpacity>

              {rewriteResult && (
                <View style={styles.rewriteResults}>
                  <Text style={styles.resultsTitle}>Versiones mejoradas:</Text>
                  {rewriteResult.versiones.map((version, index) => (
                    <View key={index} style={styles.versionCard}>
                      <Text style={styles.versionLabel}>Versión {index + 1}</Text>
                      <Text style={styles.versionText}>{version}</Text>
                      <TouchableOpacity
                        style={styles.copyVersionButton}
                        onPress={() => copyRewriteVersion(version)}
                      >
                        <Ionicons name="copy" size={16} color="#6366f1" />
                        <Text style={styles.copyVersionText}>Copiar</Text>
                      </TouchableOpacity>
                    </View>
                  ))}
                </View>
              )}
            </ScrollView>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f9fafb',
  },
  scrollView: {
    flex: 1,
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  intensitySection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24,
  },
  intensityLabel: {
    fontSize: 16,
    color: '#374151',
    marginRight: 12,
  },
  intensityBadge: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
  },
  intensityText: {
    color: '#fff',
    fontWeight: 'bold',
    fontSize: 14,
  },
  warningBox: {
    backgroundColor: '#fee2e2',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
    borderWidth: 2,
    borderColor: '#dc2626',
    alignItems: 'center',
  },
  warningTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#dc2626',
    marginTop: 8,
    marginBottom: 8,
  },
  warningText: {
    fontSize: 15,
    color: '#7f1d1d',
    textAlign: 'center',
    marginBottom: 16,
    lineHeight: 22,
  },
  warningButton: {
    backgroundColor: '#dc2626',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 8,
  },
  warningButtonText: {
    color: '#fff',
    fontWeight: '600',
  },
  section: {
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 12,
  },
  subsectionTitle: {
    fontSize: 15,
    fontWeight: '600',
    color: '#374151',
    marginTop: 12,
    marginBottom: 8,
  },
  sectionText: {
    fontSize: 15,
    color: '#4b5563',
    lineHeight: 22,
  },
  bulletItem: {
    fontSize: 15,
    color: '#4b5563',
    lineHeight: 22,
    marginBottom: 4,
  },
  actionButtons: {
    flexDirection: 'row',
    gap: 12,
    marginTop: 8,
    marginBottom: 16,
  },
  copyButton: {
    flex: 1,
    backgroundColor: '#6366f1',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  copyButtonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: '600',
    marginLeft: 8,
  },
  rewriteButton: {
    flex: 1,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#6366f1',
  },
  rewriteButtonText: {
    color: '#6366f1',
    fontSize: 15,
    fontWeight: '600',
    marginLeft: 8,
  },
  backHomeButton: {
    backgroundColor: '#f3f4f6',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  backHomeButtonText: {
    color: '#374151',
    fontSize: 15,
    fontWeight: '600',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#fff',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 20,
    maxHeight: '90%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1f2937',
  },
  modalScroll: {
    maxHeight: 500,
  },
  modalLabel: {
    fontSize: 15,
    color: '#374151',
    marginBottom: 12,
  },
  modalInput: {
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    padding: 16,
    fontSize: 15,
    color: '#1f2937',
    borderWidth: 1,
    borderColor: '#e5e7eb',
    minHeight: 100,
    marginBottom: 16,
  },
  modalButton: {
    backgroundColor: '#6366f1',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 20,
  },
  buttonDisabled: {
    opacity: 0.6,
  },
  modalButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  rewriteResults: {
    marginTop: 8,
  },
  resultsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
  },
  versionCard: {
    backgroundColor: '#f9fafb',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e5e7eb',
  },
  versionLabel: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6366f1',
    marginBottom: 8,
  },
  versionText: {
    fontSize: 15,
    color: '#1f2937',
    lineHeight: 22,
    marginBottom: 12,
  },
  copyVersionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
  },
  copyVersionText: {
    color: '#6366f1',
    fontSize: 14,
    fontWeight: '600',
    marginLeft: 4,
  },
});
