using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using System.ComponentModel.DataAnnotations;
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using System.Text.RegularExpressions;

var builder = WebApplication.CreateBuilder(args);

// Конфигурация JWT
var jwtSettings = builder.Configuration.GetSection("JwtSettings");
var secretKey = jwtSettings["SecretKey"] ?? throw new InvalidOperationException("JWT SecretKey не настроен");
var issuer = jwtSettings["Issuer"] ?? "AuthService";
var audience = jwtSettings["Audience"] ?? "AuthServiceUsers";

// Добавляем DbContext
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

// Добавляем сервисы
builder.Services.AddScoped<IAuthService, AuthService>();

// Настройка JWT аутентификации
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = issuer,
            ValidAudience = audience,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey))
        };
    });

builder.Services.AddAuthorization();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new Microsoft.OpenApi.Models.OpenApiInfo
    {
        Title = "Auth Service API",
        Version = "v1",
        Description = "API для регистрации, аутентификации и авторизации пользователей с использованием JWT токенов",
        Contact = new Microsoft.OpenApi.Models.OpenApiContact
        {
            Name = "Auth Service",
            Email = "support@authservice.com"
        }
    });

    c.AddSecurityDefinition("Bearer", new Microsoft.OpenApi.Models.OpenApiSecurityScheme
    {
        Description = "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\"",
        Name = "Authorization",
        In = Microsoft.OpenApi.Models.ParameterLocation.Header,
        Type = Microsoft.OpenApi.Models.SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    c.AddSecurityRequirement(new Microsoft.OpenApi.Models.OpenApiSecurityRequirement
    {
        {
            new Microsoft.OpenApi.Models.OpenApiSecurityScheme
            {
                Reference = new Microsoft.OpenApi.Models.OpenApiReference
                {
                    Type = Microsoft.OpenApi.Models.ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

var app = builder.Build();

using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.Migrate();
}

app.UseSwagger();
app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "Auth API V1");
    c.RoutePrefix = string.Empty; // Swagger будет на корневом URL
});

app.UseAuthentication();
app.UseAuthorization();

// Регистрация
app.MapPost("/api/auth/register", async (RegisterRequest request, IAuthService authService) =>
{
    var result = await authService.RegisterAsync(request.Email, request.Password);

    if (!result.Success)
        return Results.BadRequest(new { error = result.ErrorMessage });

    return Results.Ok(new { message = "Пользователь успешно зарегистрирован", userId = result.UserId });
})
.WithName("Register")
.WithTags("Authentication")
.WithSummary("Регистрация нового пользователя")
.WithDescription("Создает нового пользователя с указанным email и паролем. Пароль хранится в захэшированном виде.");

// Логин
app.MapPost("/api/auth/login", async (LoginRequest request, IAuthService authService) =>
{
    var result = await authService.LoginAsync(request.Email, request.Password);

    if (!result.Success)
        return Results.Unauthorized();

    return Results.Ok(new { token = result.Token, expiresAt = result.ExpiresAt });
})
.WithName("Login")
.WithTags("Authentication")
.WithSummary("Вход пользователя в систему")
.WithDescription("Аутентифицирует пользователя и возвращает JWT токен, действительный в течение 24 часов.");

app.Run();

// Модели
public record RegisterRequest(
    [property: Required(ErrorMessage = "Email обязателен")]
    [property: EmailAddress(ErrorMessage = "Некорректный формат email")]
    string Email,

    [property: Required(ErrorMessage = "Пароль обязателен")]
    [property: MinLength(6, ErrorMessage = "Пароль должен содержать минимум 6 символов")]
    string Password
);

public record LoginRequest(
    [property: Required(ErrorMessage = "Email обязателен")]
    [property: EmailAddress(ErrorMessage = "Некорректный формат email")]
    string Email,

    [property: Required(ErrorMessage = "Пароль обязателен")]
    string Password
);

// Entity
public class User
{
    public Guid Id { get; set; }

    [Required]
    [EmailAddress]
    [MaxLength(255)]
    public string Email { get; set; } = string.Empty;

    [Required]
    [MaxLength(255)]
    public string PasswordHash { get; set; } = string.Empty;

    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
}

// DbContext
public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Email).IsUnique();
            entity.Property(e => e.Email).IsRequired();
            entity.Property(e => e.PasswordHash).IsRequired();
        });
    }
}

// Интерфейс сервиса
public interface IAuthService
{
    Task<AuthResult> RegisterAsync(string email, string password);
    Task<LoginResult> LoginAsync(string email, string password);
}

// Результаты операций
public class AuthResult
{
    public bool Success { get; set; }
    public string? ErrorMessage { get; set; }
    public Guid? UserId { get; set; }
}

public class LoginResult
{
    public bool Success { get; set; }
    public string? Token { get; set; }
    public DateTime? ExpiresAt { get; set; }
}

// Реализация сервиса
public class AuthService : IAuthService
{
    private readonly AppDbContext _context;
    private readonly IConfiguration _configuration;

    public AuthService(AppDbContext context, IConfiguration configuration)
    {
        _context = context;
        _configuration = configuration;
    }

    public async Task<AuthResult> RegisterAsync(string email, string password)
    {
        // Валидация email
        if (!IsValidEmail(email))
            return new AuthResult { Success = false, ErrorMessage = "Некорректный формат email" };

        // Валидация пароля
        if (string.IsNullOrWhiteSpace(password) || password.Length < 6)
            return new AuthResult { Success = false, ErrorMessage = "Пароль должен содержать минимум 6 символов" };

        // Проверка существования пользователя
        if (await _context.Users.AnyAsync(u => u.Email == email.ToLower()))
            return new AuthResult { Success = false, ErrorMessage = "Пользователь с таким email уже существует" };

        // Хэширование пароля
        var passwordHash = HashPassword(password);

        // Создание пользователя
        var user = new User
        {
            Id = Guid.NewGuid(),
            Email = email.ToLower(),
            PasswordHash = passwordHash
        };

        _context.Users.Add(user);
        await _context.SaveChangesAsync();

        return new AuthResult { Success = true, UserId = user.Id };
    }

    public async Task<LoginResult> LoginAsync(string email, string password)
    {
        var user = await _context.Users.FirstOrDefaultAsync(u => u.Email == email.ToLower());

        if (user == null || !VerifyPassword(password, user.PasswordHash))
            return new LoginResult { Success = false };

        var token = GenerateJwtToken(user);
        var expiresAt = DateTime.UtcNow.AddHours(24);

        return new LoginResult { Success = true, Token = token, ExpiresAt = expiresAt };
    }

    private bool IsValidEmail(string email)
    {
        if (string.IsNullOrWhiteSpace(email))
            return false;

        var emailRegex = new Regex(@"^[^@\s]+@[^@\s]+\.[^@\s]+$", RegexOptions.IgnoreCase);
        return emailRegex.IsMatch(email);
    }

    private string HashPassword(string password)
    {
        using var sha256 = SHA256.Create();
        var hashedBytes = sha256.ComputeHash(Encoding.UTF8.GetBytes(password));
        return Convert.ToBase64String(hashedBytes);
    }

    private bool VerifyPassword(string password, string passwordHash)
    {
        var hash = HashPassword(password);
        return hash == passwordHash;
    }

    private string GenerateJwtToken(User user)
    {
        var jwtSettings = _configuration.GetSection("JwtSettings");
        var secretKey = jwtSettings["SecretKey"] ?? throw new InvalidOperationException("JWT SecretKey не настроен");
        var issuer = jwtSettings["Issuer"] ?? "AuthService";
        var audience = jwtSettings["Audience"] ?? "AuthServiceUsers";

        var securityKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey));
        var credentials = new SigningCredentials(securityKey, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
        };

        var token = new JwtSecurityToken(
            issuer: issuer,
            audience: audience,
            claims: claims,
            expires: DateTime.UtcNow.AddHours(24),
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}