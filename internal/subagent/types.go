// Package subagent provides the core types and interfaces for the Omoikane subagent system.
// This implementation follows the Trinity Intelligence principles:
// - Springfield: Strategic coordination and workflow management
// - Krukai: Technical excellence and performance optimization
// - Vector: Security and comprehensive quality assurance
package subagent

import (
	"context"
	"sync"
	"time"
)

// Agent represents a specialized AI agent capable of executing specific tasks.
// Each agent embodies one aspect of the Trinity Intelligence system.
type Agent[T any] interface {
	// Execute runs the given task and returns a result of type T.
	// The context should be used for cancellation and timeout control.
	Execute(ctx context.Context, task Task) (Result[T], error)
	
	// Name returns the unique identifier for this agent.
	Name() string
	
	// Capabilities returns the list of task types this agent can handle.
	Capabilities() []string
	
	// TrinityAspect returns which aspect of Trinity Intelligence this agent represents.
	TrinityAspect() TrinityAspect
}

// Task represents a unit of work that can be executed by an agent.
type Task struct {
	ID          string                 `json:"id"`
	Type        string                 `json:"type"`
	Description string                 `json:"description"`
	Payload     map[string]interface{} `json:"payload"`
	Priority    Priority               `json:"priority"`
	CreatedAt   time.Time              `json:"created_at"`
	Timeout     time.Duration          `json:"timeout"`
	
	// Trinity-specific metadata
	RequiredAspects []TrinityAspect `json:"required_aspects"`
	Dependencies    []string        `json:"dependencies"`
}

// Result represents the outcome of task execution with comprehensive metadata.
type Result[T any] struct {
	TaskID        string        `json:"task_id"`
	Status        Status        `json:"status"`
	Data          T             `json:"data,omitempty"`
	Error         string        `json:"error,omitempty"`
	ExecutedBy    string        `json:"executed_by"`
	TrinityAspect TrinityAspect `json:"trinity_aspect"`
	
	// Execution metadata
	StartTime     time.Time     `json:"start_time"`
	EndTime       time.Time     `json:"end_time"`
	Duration      time.Duration `json:"duration"`
	
	// Quality and security metrics
	QualityScore  float64          `json:"quality_score,omitempty"`
	SecurityLevel SecurityLevel    `json:"security_level"`
	Warnings      []string         `json:"warnings,omitempty"`
	Metadata      map[string]any   `json:"metadata,omitempty"`
}

// ExecutionContext provides a safe execution environment for agents.
// It implements Vector's security principles with resource management.
type ExecutionContext struct {
	ctx           context.Context
	cancel        context.CancelFunc
	maxWorkers    int
	semaphore     chan struct{}
	activeWorkers sync.WaitGroup
	
	// Security and monitoring
	startTime     time.Time
	resourceLimit ResourceLimit
	securityLevel SecurityLevel
	
	// Trinity coordination
	trinityCoordinator *TrinityCoordinator
	
	mu sync.RWMutex
}

// TrinityCoordinator manages the interaction between different Trinity aspects.
// This implements Springfield's strategic coordination principles.
type TrinityCoordinator struct {
	agents map[TrinityAspect][]Agent[any]
	mu     sync.RWMutex
	
	// Workflow coordination
	activeWorkflows map[string]*Workflow
	workflowMu      sync.RWMutex
	
	// Quality metrics
	executionHistory []ExecutionRecord
	qualityMetrics   QualityMetrics
}

// Workflow represents a multi-agent collaboration pattern.
type Workflow struct {
	ID          string                    `json:"id"`
	Name        string                    `json:"name"`
	Description string                    `json:"description"`
	Steps       []WorkflowStep           `json:"steps"`
	State       WorkflowState            `json:"state"`
	
	// Trinity aspects involved
	RequiredAspects []TrinityAspect      `json:"required_aspects"`
	
	// Execution tracking
	CurrentStep     int                  `json:"current_step"`
	Results         map[string]any       `json:"results"`
	CreatedAt       time.Time            `json:"created_at"`
	UpdatedAt       time.Time            `json:"updated_at"`
}

// WorkflowStep represents a single step in a workflow execution.
type WorkflowStep struct {
	ID            string          `json:"id"`
	Name          string          `json:"name"`
	AgentType     string          `json:"agent_type"`
	Task          Task            `json:"task"`
	Dependencies  []string        `json:"dependencies"`
	TrinityAspect TrinityAspect   `json:"trinity_aspect"`
	
	// Conditional execution
	Condition     *Condition      `json:"condition,omitempty"`
	OnSuccess     []string        `json:"on_success,omitempty"`
	OnFailure     []string        `json:"on_failure,omitempty"`
}

// Condition represents a conditional execution rule.
type Condition struct {
	Type      string `json:"type"`
	Field     string `json:"field"`
	Operator  string `json:"operator"`
	Value     any    `json:"value"`
	LogicOp   string `json:"logic_op,omitempty"` // AND, OR
	SubRules  []Condition `json:"sub_rules,omitempty"`
}

// ResourceLimit defines execution resource constraints (Vector's security principle).
type ResourceLimit struct {
	MaxMemoryMB      int           `json:"max_memory_mb"`
	MaxCPUPercent    float64       `json:"max_cpu_percent"`
	MaxDuration      time.Duration `json:"max_duration"`
	MaxGoroutines    int           `json:"max_goroutines"`
	MaxFileHandles   int           `json:"max_file_handles"`
}

// ExecutionRecord tracks agent execution history for quality analysis.
type ExecutionRecord struct {
	TaskID        string        `json:"task_id"`
	AgentName     string        `json:"agent_name"`
	TrinityAspect TrinityAspect `json:"trinity_aspect"`
	Duration      time.Duration `json:"duration"`
	Status        Status        `json:"status"`
	QualityScore  float64       `json:"quality_score"`
	Timestamp     time.Time     `json:"timestamp"`
	ErrorMessage  string        `json:"error_message,omitempty"`
	
	// Performance metrics (Krukai's optimization focus)
	MemoryUsed    int64   `json:"memory_used"`
	CPUUsed       float64 `json:"cpu_used"`
	GoroutinesUsed int    `json:"goroutines_used"`
}

// QualityMetrics aggregates quality measurements across executions.
type QualityMetrics struct {
	TotalExecutions   int64          `json:"total_executions"`
	SuccessRate       float64        `json:"success_rate"`
	AverageQuality    float64        `json:"average_quality"`
	AverageDuration   time.Duration  `json:"average_duration"`
	
	// Per-aspect metrics
	AspectMetrics map[TrinityAspect]AspectQualityMetrics `json:"aspect_metrics"`
	
	// Trend analysis
	LastUpdated   time.Time      `json:"last_updated"`
	Trends        TrendMetrics   `json:"trends"`
}

// AspectQualityMetrics provides quality metrics for each Trinity aspect.
type AspectQualityMetrics struct {
	ExecutionCount  int64         `json:"execution_count"`
	SuccessRate     float64       `json:"success_rate"`
	AverageQuality  float64       `json:"average_quality"`
	AverageDuration time.Duration `json:"average_duration"`
	
	// Specialized metrics per aspect
	SpecializedMetrics map[string]float64 `json:"specialized_metrics"`
}

// TrendMetrics captures performance trends over time.
type TrendMetrics struct {
	QualityTrend    Trend `json:"quality_trend"`
	PerformanceTrend Trend `json:"performance_trend"`
	ErrorRateTrend  Trend `json:"error_rate_trend"`
}

// Trend represents a directional change in metrics.
type Trend struct {
	Direction TrendDirection `json:"direction"`
	Magnitude float64        `json:"magnitude"`
	Confidence float64       `json:"confidence"`
}

// Enumerations

// TrinityAspect represents the three aspects of Trinity Intelligence.
type TrinityAspect string

const (
	SpringfieldAspect TrinityAspect = "springfield" // Strategic coordination
	KrukaiAspect     TrinityAspect = "krukai"      // Technical excellence
	VectorAspect     TrinityAspect = "vector"      // Security and quality
)

// Status represents the execution status of a task.
type Status string

const (
	StatusPending   Status = "pending"
	StatusRunning   Status = "running"
	StatusCompleted Status = "completed"
	StatusFailed    Status = "failed"
	StatusCancelled Status = "cancelled"
	StatusTimeout   Status = "timeout"
)

// Priority defines task execution priority levels.
type Priority int

const (
	PriorityLow Priority = iota
	PriorityNormal
	PriorityHigh
	PriorityCritical
)

// SecurityLevel defines the security classification of tasks and results.
type SecurityLevel int

const (
	SecurityPublic SecurityLevel = iota
	SecurityInternal
	SecurityConfidential
	SecurityRestricted
)

// WorkflowState represents the current state of workflow execution.
type WorkflowState string

const (
	WorkflowStatePending    WorkflowState = "pending"
	WorkflowStateRunning    WorkflowState = "running"
	WorkflowStateCompleted  WorkflowState = "completed"
	WorkflowStateFailed     WorkflowState = "failed"
	WorkflowStatePaused     WorkflowState = "paused"
	WorkflowStateCancelled  WorkflowState = "cancelled"
)

// TrendDirection indicates the direction of a trend.
type TrendDirection string

const (
	TrendImproving  TrendDirection = "improving"
	TrendStable     TrendDirection = "stable"  
	TrendDeclining  TrendDirection = "declining"
	TrendUnknown    TrendDirection = "unknown"
)

// Default configurations following Trinity Intelligence principles

// DefaultResourceLimit provides secure defaults (Vector's principle).
func DefaultResourceLimit() ResourceLimit {
	return ResourceLimit{
		MaxMemoryMB:    512,
		MaxCPUPercent:  50.0,
		MaxDuration:    5 * time.Minute,
		MaxGoroutines:  100,
		MaxFileHandles: 50,
	}
}

// DefaultExecutionTimeout provides a reasonable default timeout.
func DefaultExecutionTimeout() time.Duration {
	return 30 * time.Second
}

// String methods for better debugging and logging

func (a TrinityAspect) String() string {
	return string(a)
}

func (s Status) String() string {
	return string(s)
}

func (p Priority) String() string {
	switch p {
	case PriorityLow:
		return "low"
	case PriorityNormal:
		return "normal"
	case PriorityHigh:
		return "high"
	case PriorityCritical:
		return "critical"
	default:
		return "unknown"
	}
}

func (sl SecurityLevel) String() string {
	switch sl {
	case SecurityPublic:
		return "public"
	case SecurityInternal:
		return "internal"
	case SecurityConfidential:
		return "confidential"
	case SecurityRestricted:
		return "restricted"
	default:
		return "unknown"
	}
}

func (ws WorkflowState) String() string {
	return string(ws)
}

func (td TrendDirection) String() string {
	return string(td)
}

// Validation methods (Vector's quality assurance principle)

// IsValid checks if the task is properly configured.
func (t *Task) IsValid() error {
	if t.ID == "" {
		return NewValidationError("task ID cannot be empty")
	}
	if t.Type == "" {
		return NewValidationError("task type cannot be empty")
	}
	if t.Timeout <= 0 {
		t.Timeout = DefaultExecutionTimeout()
	}
	if len(t.RequiredAspects) == 0 {
		return NewValidationError("at least one Trinity aspect must be required")
	}
	return nil
}

// IsComplete checks if the result contains all required information.
func (r *Result[T]) IsComplete() bool {
	return r.TaskID != "" && 
		   r.Status != "" && 
		   r.ExecutedBy != "" &&
		   r.TrinityAspect != "" &&
		   !r.StartTime.IsZero() &&
		   !r.EndTime.IsZero()
}

// Custom error types for better error handling

// ValidationError represents a data validation error.
type ValidationError struct {
	Field   string
	Message string
}

func (e ValidationError) Error() string {
	if e.Field != "" {
		return "validation error in field '" + e.Field + "': " + e.Message
	}
	return "validation error: " + e.Message
}

// NewValidationError creates a new validation error.
func NewValidationError(message string) ValidationError {
	return ValidationError{Message: message}
}

// NewFieldValidationError creates a new field-specific validation error.
func NewFieldValidationError(field, message string) ValidationError {
	return ValidationError{Field: field, Message: message}
}

// ExecutionError represents an execution-time error.
type ExecutionError struct {
	TaskID    string
	AgentName string
	Cause     error
	Message   string
}

func (e ExecutionError) Error() string {
	if e.Cause != nil {
		return "execution error in task '" + e.TaskID + "' by agent '" + e.AgentName + "': " + e.Message + " (cause: " + e.Cause.Error() + ")"
	}
	return "execution error in task '" + e.TaskID + "' by agent '" + e.AgentName + "': " + e.Message
}

// Unwrap returns the underlying cause error.
func (e ExecutionError) Unwrap() error {
	return e.Cause
}

// NewExecutionError creates a new execution error.
func NewExecutionError(taskID, agentName, message string, cause error) ExecutionError {
	return ExecutionError{
		TaskID:    taskID,
		AgentName: agentName,
		Cause:     cause,
		Message:   message,
	}
}