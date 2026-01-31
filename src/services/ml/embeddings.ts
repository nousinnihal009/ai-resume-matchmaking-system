/**
 * Embedding Generation Service
 * Generates semantic vector embeddings for text
 * Simulates sentence transformers / BERT-based embeddings
 */

import { logger } from '@/utils/logger';
import { AppConfig } from '@/config/app.config';

const EMBEDDING_DIM = AppConfig.ml.embeddingDimension;

/**
 * Generate embedding vector for text
 * In production, this would call a real ML model (sentence-transformers, OpenAI, etc.)
 */
export async function generateEmbedding(text: string): Promise<number[]> {
  logger.debug('Generating embedding', { textLength: text.length });

  // Simulate async API call to embedding model
  await new Promise(resolve => setTimeout(resolve, 100));

  // For demonstration, we generate a deterministic "embedding" based on text features
  // In production, use: sentence-transformers, OpenAI embeddings, or custom BERT models
  const embedding = simulateEmbedding(text);

  logger.debug('Embedding generated', { dimension: embedding.length });

  return embedding;
}

/**
 * Batch generate embeddings for multiple texts
 */
export async function batchGenerateEmbeddings(texts: string[]): Promise<number[][]> {
  logger.info('Batch generating embeddings', { count: texts.length });

  // In production, use batch processing for efficiency
  const embeddings = await Promise.all(texts.map(text => generateEmbedding(text)));

  logger.info('Batch embeddings completed');

  return embeddings;
}

/**
 * Simulate embedding generation using text features
 * This creates a deterministic "embedding" for demonstration purposes
 */
function simulateEmbedding(text: string): number[] {
  const normalizedText = text.toLowerCase();
  const embedding = new Array(EMBEDDING_DIM).fill(0);

  // Create a pseudo-embedding based on text characteristics
  // This is purely for demonstration - real embeddings capture semantic meaning

  // Character frequency features (first 26 dimensions)
  for (let i = 0; i < 26; i++) {
    const char = String.fromCharCode(97 + i); // a-z
    const count = (normalizedText.match(new RegExp(char, 'g')) || []).length;
    embedding[i] = count / Math.max(text.length, 1);
  }

  // Word-based features
  const words = normalizedText.split(/\s+/);
  const uniqueWords = new Set(words);

  // Lexical diversity (dimension 26-30)
  embedding[26] = uniqueWords.size / Math.max(words.length, 1);
  embedding[27] = words.length / 100; // Normalized length
  embedding[28] = (normalizedText.match(/[.!?]/g) || []).length / 10;
  
  // Technical keyword presence (dimension 30-100)
  const technicalKeywords = [
    'python', 'javascript', 'java', 'react', 'node', 'database', 'api',
    'cloud', 'aws', 'docker', 'machine learning', 'ai', 'data', 'backend',
    'frontend', 'full stack', 'devops', 'agile', 'git', 'sql', 'nosql',
    'microservices', 'kubernetes', 'terraform', 'ci/cd', 'rest', 'graphql',
    'typescript', 'mongodb', 'postgresql', 'redis', 'kafka', 'spark',
    'tensorflow', 'pytorch', 'numpy', 'pandas', 'scikit-learn', 'django',
    'flask', 'fastapi', 'express', 'spring', 'angular', 'vue', 'next.js',
    'redux', 'oauth', 'jwt', 'security', 'testing', 'unit test', 'integration',
  ];

  for (let i = 0; i < Math.min(technicalKeywords.length, 70); i++) {
    const keyword = technicalKeywords[i];
    embedding[30 + i] = normalizedText.includes(keyword) ? 1.0 : 0.0;
  }

  // Soft skill presence (dimension 100-120)
  const softSkillKeywords = [
    'leadership', 'communication', 'team', 'collaboration', 'problem solving',
    'critical thinking', 'analytical', 'creative', 'innovative', 'motivated',
    'organized', 'detail oriented', 'time management', 'adaptable', 'flexible',
    'mentor', 'coach', 'presentation', 'documentation', 'research',
  ];

  for (let i = 0; i < Math.min(softSkillKeywords.length, 20); i++) {
    const keyword = softSkillKeywords[i];
    embedding[100 + i] = normalizedText.includes(keyword) ? 1.0 : 0.0;
  }

  // Educational indicators (dimension 120-130)
  const educationKeywords = [
    'university', 'college', 'bachelor', 'master', 'phd', 'degree',
    'graduate', 'gpa', 'coursework', 'research',
  ];

  for (let i = 0; i < educationKeywords.length; i++) {
    const keyword = educationKeywords[i];
    embedding[120 + i] = normalizedText.includes(keyword) ? 1.0 : 0.0;
  }

  // Experience indicators (dimension 130-140)
  const experienceKeywords = [
    'intern', 'experience', 'years', 'developed', 'implemented', 'designed',
    'built', 'created', 'managed', 'led',
  ];

  for (let i = 0; i < experienceKeywords.length; i++) {
    const keyword = experienceKeywords[i];
    embedding[130 + i] = normalizedText.includes(keyword) ? 1.0 : 0.0;
  }

  // Fill remaining dimensions with noise based on text hash
  let hash = 0;
  for (let i = 0; i < text.length; i++) {
    hash = ((hash << 5) - hash) + text.charCodeAt(i);
    hash = hash & hash; // Convert to 32-bit integer
  }

  for (let i = 140; i < EMBEDDING_DIM; i++) {
    // Use hash to generate deterministic pseudo-random values
    hash = (hash * 1103515245 + 12345) & 0x7fffffff;
    embedding[i] = (hash % 1000) / 1000 - 0.5;
  }

  // Normalize the embedding vector
  return normalizeVector(embedding);
}

/**
 * Normalize vector to unit length
 */
function normalizeVector(vector: number[]): number[] {
  const magnitude = Math.sqrt(vector.reduce((sum, val) => sum + val * val, 0));
  if (magnitude === 0) return vector;
  return vector.map(val => val / magnitude);
}

/**
 * Calculate cosine similarity between two embeddings
 */
export function cosineSimilarity(embedding1: number[], embedding2: number[]): number {
  if (embedding1.length !== embedding2.length) {
    throw new Error('Embeddings must have the same dimension');
  }

  let dotProduct = 0;
  let norm1 = 0;
  let norm2 = 0;

  for (let i = 0; i < embedding1.length; i++) {
    dotProduct += embedding1[i] * embedding2[i];
    norm1 += embedding1[i] * embedding1[i];
    norm2 += embedding2[i] * embedding2[i];
  }

  if (norm1 === 0 || norm2 === 0) return 0;

  return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
}

/**
 * Calculate Euclidean distance between two embeddings
 */
export function euclideanDistance(embedding1: number[], embedding2: number[]): number {
  if (embedding1.length !== embedding2.length) {
    throw new Error('Embeddings must have the same dimension');
  }

  let sumSquares = 0;
  for (let i = 0; i < embedding1.length; i++) {
    const diff = embedding1[i] - embedding2[i];
    sumSquares += diff * diff;
  }

  return Math.sqrt(sumSquares);
}

/**
 * Calculate dot product between two embeddings
 */
export function dotProduct(embedding1: number[], embedding2: number[]): number {
  if (embedding1.length !== embedding2.length) {
    throw new Error('Embeddings must have the same dimension');
  }

  let product = 0;
  for (let i = 0; i < embedding1.length; i++) {
    product += embedding1[i] * embedding2[i];
  }

  return product;
}

/**
 * Find top K most similar embeddings using cosine similarity
 */
export function findTopKSimilar(
  queryEmbedding: number[],
  candidateEmbeddings: Array<{ id: string; embedding: number[] }>,
  k: number
): Array<{ id: string; similarity: number }> {
  logger.debug('Finding top K similar embeddings', { k, candidates: candidateEmbeddings.length });

  const similarities = candidateEmbeddings.map(candidate => ({
    id: candidate.id,
    similarity: cosineSimilarity(queryEmbedding, candidate.embedding),
  }));

  // Sort by similarity descending and take top K
  similarities.sort((a, b) => b.similarity - a.similarity);

  return similarities.slice(0, k);
}

/**
 * Average multiple embeddings
 */
export function averageEmbeddings(embeddings: number[][]): number[] {
  if (embeddings.length === 0) {
    throw new Error('Cannot average empty embedding list');
  }

  const dim = embeddings[0].length;
  const avg = new Array(dim).fill(0);

  for (const embedding of embeddings) {
    for (let i = 0; i < dim; i++) {
      avg[i] += embedding[i];
    }
  }

  for (let i = 0; i < dim; i++) {
    avg[i] /= embeddings.length;
  }

  return normalizeVector(avg);
}
